#!/usr/bin/env python3
"""
Symbol Table Implementation for Pascal-S Semantic Analysis

This module implements the symbol table structure required for semantic analysis
of Pascal-S programs. It maintains three main tables:
- tab: identifier table (variables, constants, procedures, functions, types)
- btab: block table (program blocks, procedure/function scopes)
- atab: array table (array type information)

The symbol table supports scope management with proper lexical scoping rules
and provides lookup functionality that follows the scope chain.

Compatible with AST nodes defined in ast_nodes.py.
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, ConstDeclNode, TypeDeclNode,
    ProcedureDeclNode, FunctionDeclNode, PrimitiveTypeNode, ArrayTypeNode,
    CustomTypeNode, RangeTypeNode, TypeSpecNode
)


class ObjectType(Enum):
    """Object types for symbol table entries"""
    CONSTANT = "constant"
    VARIABLE = "variable" 
    TYPE = "type"
    PROCEDURE = "procedure"
    FUNCTION = "function"
    PROGRAM = "program"
    PARAMETER = "parameter"


class DataType(Enum):
    """
    Data types supported by Pascal-S
    Mapped to integer indices for typ field in symbol table:
    0 = procedure (void)
    1 = int (integer)
    2 = real
    3 = bool (boolean)
    4 = char
    5 = array
    6 = complex (string/custom)
    """
    VOID = 0       # procedure
    INTEGER = 1    # int
    REAL = 2       # real
    BOOLEAN = 3    # bool
    CHAR = 4       # char
    ARRAY = 5      # array
    STRING = 6     # complex (string)
    CUSTOM = 6     # complex (custom types)


class SymbolTableEntry:
    """
    Entry in the identifier table (tab).
    
    Fields:
    - id: identifier name
    - obj: object type (constant, variable, procedure, etc.)
    - type: data type 
    - ref: reference to other table entries (for arrays, procedures, etc.)
    - nrm: normal/reference parameter (True for value, False for reference)
    - lev: lexical level (0=global, 1=first nested level, etc.)
    - adr: address/offset in memory
    - link: link to previous symbol in same scope (for scope chain)
    """
    
    def __init__(
        self,
        id: str,
        obj: ObjectType,
        type: DataType,
        ref: int = -1,
        nrm: bool = True,
        lev: int = 0,
        adr: int = 0,
        link: int = -1
    ):
        self.id = id
        self.obj = obj
        self.type = type
        self.ref = ref
        self.nrm = nrm
        self.lev = lev
        self.adr = adr
        self.link = link
    
    def __repr__(self):
        return (f"SymbolTableEntry(id='{self.id}', obj={self.obj.value}, "
                f"type={self.type.value}, ref={self.ref}, nrm={self.nrm}, "
                f"lev={self.lev}, adr={self.adr}, link={self.link})")


class BlockTableEntry:
    """
    Entry in the block table (btab).
    
    Fields:
    - last: index of last identifier in this block
    - lastpar: index of last parameter in this block
    - psize: size of parameters
    - vsize: size of local variables
    """
    
    def __init__(
        self,
        last: int = -1,
        lastpar: int = -1,
        psize: int = 0,
        vsize: int = 0
    ):
        self.last = last
        self.lastpar = lastpar
        self.psize = psize
        self.vsize = vsize
    
    def __repr__(self):
        return (f"BlockTableEntry(last={self.last}, lastpar={self.lastpar}, "
                f"psize={self.psize}, vsize={self.vsize})")


class ArrayTableEntry:
    """
    Entry in the array table (atab).
    
    Fields:
    - inxtyp: index type
    - eltyp: element type
    - elref: element reference (for nested arrays)
    - low: lower bound
    - high: upper bound
    - elsize: element size
    - size: total array size
    """
    
    def __init__(
        self,
        inxtyp: DataType,
        eltyp: DataType,
        elref: int = -1,
        low: int = 0,
        high: int = 0,
        elsize: int = 1,
        size: int = 0
    ):
        self.inxtyp = inxtyp
        self.eltyp = eltyp
        self.elref = elref
        self.low = low
        self.high = high
        self.elsize = elsize
        self.size = size
    
    def __repr__(self):
        return (f"ArrayTableEntry(inxtyp={self.inxtyp.value}, eltyp={self.eltyp.value}, "
                f"elref={self.elref}, low={self.low}, high={self.high}, "
                f"elsize={self.elsize}, size={self.size})")


class SymbolTable:
    """
    Complete symbol table implementation for Pascal-S semantic analysis.
    
    Manages three main tables:
    - tab: identifier table (indices 0-31 reserved for reserved words, user identifiers start at 32)
    - btab: block table  
    - atab: array table
    
    Provides scope management and symbol lookup functionality.
    
    Note: According to Pascal-S specification, tab indices 0-31 are reserved
    for reserved words. User-defined identifiers start at index 32.
    """
    
    # Reserved word count - indices 0-31 are reserved
    RESERVED_COUNT = 32
    
    def __init__(self):
        # Main symbol tables
        self.tab: List[Optional[SymbolTableEntry]] = []  # identifier table
        self.btab: List[BlockTableEntry] = []            # block table
        self.atab: List[ArrayTableEntry] = []            # array table
        
        # Current state
        self.current_level = 0          # current lexical level
        self.current_block = -1         # current block index
        self.next_address = 0           # next available address
        self.display: List[int] = []    # scope display stack
        
        # Reserved words list (indices 0-31) - Indonesian keywords
        self.RESERVED_WORDS = [
            # Keywords (26)
            "program", "variabel", "mulai", "selesai", "jika", 
            "maka", "selain-itu", "selama", "lakukan", "untuk",
            "ke", "turun-ke", "integer", "real", "boolean",
            "char", "larik", "dari", "prosedur", "fungsi",
            "konstanta", "tipe", "string", "kasus", "ulangi",
            "sampai", "rekaman",
            # Logical operators (3)
            "dan", "atau", "tidak",
            # Arithmetic operators (2)
            "bagi", "mod"
        ]
        
        # Pre-fill tab with reserved entries (indices 0-28)
        self._initialize_reserved_entries()
        
        # Initialize with built-in types and procedures
        self._initialize_builtins()
    
    def _initialize_reserved_entries(self):
        """
        Pre-fill symbol table with 32 reserved entries (indices 0-31).
        These are reserved for Pascal-S Indonesian reserved words.
        User-defined identifiers will start at index 32.
        """
        # Fill indices 0-31 with reserved word entries
        for i, word in enumerate(self.RESERVED_WORDS):
            entry = SymbolTableEntry(
                id=word,
                obj=ObjectType.TYPE,  # Reserved words are keywords
                type=DataType.VOID,
                ref=-1,
                nrm=True,
                lev=0,
                adr=0,
                link=-1
            )
            self.tab.append(entry)
    
    def _initialize_builtins(self):
        """Initialize symbol table with built-in procedures"""
        
        # Start global scope
        self.enter_block()
    
    def enter_block(self) -> int:
        """
        Enter a new block (scope).
        Returns the block index.
        """
        block_entry = BlockTableEntry()
        self.btab.append(block_entry)
        block_index = len(self.btab) - 1
        
        # Update display stack
        if len(self.display) <= self.current_level:
            self.display.extend([-1] * (self.current_level - len(self.display) + 1))
        self.display[self.current_level] = len(self.tab)
        
        self.current_block = block_index
        return block_index
    
    def exit_block(self):
        """
        Exit current block and restore previous scope.
        """
        if self.current_block >= 0:
            # Update block table with final information
            current_block_entry = self.btab[self.current_block]
            if len(self.tab) > 0:
                current_block_entry.last = len(self.tab) - 1
        
        # Restore previous level
        if self.current_level > 0:
            self.current_level -= 1
        
        # Find previous block
        self.current_block = -1
        for i in range(len(self.btab) - 2, -1, -1):
            if i < len(self.btab) - 1:
                self.current_block = i
                break
    
    # Alias methods for convenience
    def enter_scope(self) -> int:
        """Alias for enter_block() - Enter a new scope."""
        return self.enter_block()
    
    def exit_scope(self):
        """Alias for exit_block() - Exit current scope."""
        self.exit_block()
    
    def enter_procedure(self, name: str, return_type: DataType, level: int = None) -> int:
        """Enter a procedure or function into symbol table"""
        if level is None:
            level = self.current_level
            
        # Create new block for procedure
        self.current_level += 1
        block_index = self.enter_block()
        
        # Add procedure entry to symbol table
        entry = SymbolTableEntry(
            id=name,
            obj=ObjectType.PROCEDURE if return_type == DataType.VOID else ObjectType.FUNCTION,
            type=return_type,
            ref=block_index,
            lev=level,
            adr=0,
            link=self._get_current_scope_link()
        )
        
        self.tab.append(entry)
        return len(self.tab) - 1
    
    def enter_variable(self, name: str, data_type: DataType, array_ref: int = -1) -> int:
        """Enter a variable into symbol table"""
        entry = SymbolTableEntry(
            id=name,
            obj=ObjectType.VARIABLE,
            type=data_type,
            ref=array_ref,
            lev=self.current_level,
            adr=self.next_address,
            link=self._get_current_scope_link()
        )
        
        self.tab.append(entry)
        self.next_address += self._get_type_size(data_type, array_ref)
        return len(self.tab) - 1
    
    def enter_program(self, name: str) -> int:
        """Enter a program name into symbol table"""
        entry = SymbolTableEntry(
            id=name,
            obj=ObjectType.PROGRAM,
            type=DataType.VOID,
            ref=-1,
            lev=self.current_level,
            adr=0,
            link=self._get_current_scope_link()
        )
        
        self.tab.append(entry)
        return len(self.tab) - 1
    
    def enter_constant(self, name: str, data_type: DataType, value: Any) -> int:
        """Enter a constant into symbol table"""
        entry = SymbolTableEntry(
            id=name,
            obj=ObjectType.CONSTANT,
            type=data_type,
            ref=0,  # Store value hash as ref
            lev=self.current_level,
            adr=0,  # Constants don't need address
            link=self._get_current_scope_link()
        )
        
        self.tab.append(entry)
        return len(self.tab) - 1
    
    def enter_type(self, name: str, type_def: DataType, ref: int = -1) -> int:
        """Enter a type definition into symbol table"""
        entry = SymbolTableEntry(
            id=name,
            obj=ObjectType.TYPE,
            type=type_def,
            ref=ref,
            lev=self.current_level,
            adr=0,
            link=self._get_current_scope_link()
        )
        
        self.tab.append(entry)
        return len(self.tab) - 1
    
    def enter_parameter(self, name: str, data_type: DataType, by_reference: bool = False) -> int:
        """Enter a parameter into symbol table"""
        entry = SymbolTableEntry(
            id=name,
            obj=ObjectType.PARAMETER,
            type=data_type,
            nrm=not by_reference,  # nrm=True for value params, False for reference
            lev=self.current_level,
            adr=self.next_address,
            link=self._get_current_scope_link()
        )
        
        self.tab.append(entry)
        self.next_address += self._get_type_size(data_type)
        
        # Update block table with parameter info
        if self.current_block >= 0:
            self.btab[self.current_block].lastpar = len(self.tab) - 1
            self.btab[self.current_block].psize += self._get_type_size(data_type)
        
        return len(self.tab) - 1
    
    def enter_array(self, index_type: DataType, element_type: DataType, 
                   low: int, high: int, element_ref: int = -1) -> int:
        """Enter an array type into array table"""
        element_size = self._get_type_size(element_type, element_ref)
        array_size = element_size * (high - low + 1)
        
        entry = ArrayTableEntry(
            inxtyp=index_type,
            eltyp=element_type,
            elref=element_ref,
            low=low,
            high=high,
            elsize=element_size,
            size=array_size
        )
        
        self.atab.append(entry)
        return len(self.atab) - 1
    
    def lookup(self, name: str) -> Optional[SymbolTableEntry]:
        """
        Look up a symbol in the current scope and parent scopes.
        Follows the scope chain using the link attribute.
        
        Returns:
            SymbolTableEntry if found, None otherwise
        """
        # Start from the most recent symbol in current scope
        if len(self.tab) == 0:
            return None
        
        # Find the start of current scope
        current_scope_start = self.RESERVED_COUNT  # Skip reserved entries
        if (self.current_level < len(self.display) and 
            self.display[self.current_level] >= 0):
            current_scope_start = max(self.RESERVED_COUNT, self.display[self.current_level])
        
        # Search from most recent symbol backwards (skip None entries)
        for i in range(len(self.tab) - 1, self.RESERVED_COUNT - 1, -1):
            entry = self.tab[i]
            if entry is None:
                continue  # Skip reserved/None entries
            if entry.id == name:
                # Check if this entry is accessible from current scope
                if entry.lev <= self.current_level:
                    return entry
        
        return None
    
    def lookup_with_index(self, name: str) -> tuple:
        """
        Look up a symbol and return both the entry and its index.
        
        Returns:
            tuple: (SymbolTableEntry, index) if found, (None, -1) otherwise
        """
        if len(self.tab) == 0:
            return (None, -1)
        
        # Search from most recent symbol backwards (skip None entries)
        for i in range(len(self.tab) - 1, self.RESERVED_COUNT - 1, -1):
            entry = self.tab[i]
            if entry is None:
                continue
            if entry.id == name:
                if entry.lev <= self.current_level:
                    return (entry, i)
        
        return (None, -1)
    
    def lookup_in_current_scope(self, name: str) -> Optional[SymbolTableEntry]:
        """
        Look up a symbol only in the current scope (for duplicate checking).
        
        Returns:
            SymbolTableEntry if found in current scope, None otherwise
        """
        current_scope_start = self.RESERVED_COUNT
        if (self.current_level < len(self.display) and 
            self.display[self.current_level] >= 0):
            current_scope_start = max(self.RESERVED_COUNT, self.display[self.current_level])
        
        # Search only in current scope (skip None entries)
        for i in range(len(self.tab) - 1, current_scope_start - 1, -1):
            entry = self.tab[i]
            if entry is None:
                continue
            if entry.id == name and entry.lev == self.current_level:
                return entry
        
        return None
    
    def _get_current_scope_link(self) -> int:
        """Get the link to the previous symbol in the current scope"""
        if len(self.tab) <= self.RESERVED_COUNT:
            return -1
        
        # Find the most recent symbol in the current scope (skip None entries)
        for i in range(len(self.tab) - 1, self.RESERVED_COUNT - 1, -1):
            entry = self.tab[i]
            if entry is None:
                continue
            if entry.lev == self.current_level:
                return i
        
        return -1
    
    def _get_type_size(self, data_type: DataType, array_ref: int = -1) -> int:
        """Get the size of a data type in memory units"""
        if data_type == DataType.ARRAY and array_ref >= 0 and array_ref < len(self.atab):
            return self.atab[array_ref].size
        elif data_type in [DataType.INTEGER, DataType.BOOLEAN]:
            return 1
        elif data_type == DataType.REAL:
            return 2
        elif data_type == DataType.CHAR:
            return 1
        elif data_type == DataType.STRING:
            return 4  # Assume string pointer
        else:
            return 1  # Default size
    
    def get_symbol_info(self, index: int) -> Optional[SymbolTableEntry]:
        """Get symbol table entry by index"""
        if 0 <= index < len(self.tab):
            return self.tab[index]
        return None
    
    def get_array_info(self, index: int) -> Optional[ArrayTableEntry]:
        """Get array table entry by index"""
        if 0 <= index < len(self.atab):
            return self.atab[index]
        return None
    
    def get_block_info(self, index: int) -> Optional[BlockTableEntry]:
        """Get block table entry by index"""
        if 0 <= index < len(self.btab):
            return self.btab[index]
        return None
    
    def print_table(self, table_name: str = "all"):
        """Print symbol table contents for debugging"""
        if table_name in ["all", "tab"]:
            print(f"\n=== IDENTIFIER TABLE (tab) ===")
            print(f"Note: Indices 0-{self.RESERVED_COUNT-1} are reserved for Indonesian reserved words")
            for i, entry in enumerate(self.tab):
                if entry is None:
                    if i < self.RESERVED_COUNT:
                        print(f"{i:3d}: <reserved>")
                    else:
                        print(f"{i:3d}: None")
                else:
                    print(f"{i:3d}: {entry}")
        
        if table_name in ["all", "btab"]:
            print("\n=== BLOCK TABLE (btab) ===")
            for i, entry in enumerate(self.btab):
                print(f"{i:3d}: {entry}")
        
        if table_name in ["all", "atab"]:
            print("\n=== ARRAY TABLE (atab) ===")
            for i, entry in enumerate(self.atab):
                print(f"{i:3d}: {entry}")
        
        print(f"\nCurrent Level: {self.current_level}")
        print(f"Current Block: {self.current_block}")
        print(f"Next Address: {self.next_address}")
        print(f"Display Stack: {self.display}")
        print(f"First user identifier index: {self.RESERVED_COUNT}")


def data_type_from_ast(type_node: TypeSpecNode) -> DataType:
    """
    Convert AST type node to DataType enum.
    
    Args:
        type_node: AST node representing a type
        
    Returns:
        DataType enum value
    """
    if isinstance(type_node, PrimitiveTypeNode):
        type_map = {
            "integer": DataType.INTEGER,
            "real": DataType.REAL,
            "boolean": DataType.BOOLEAN,
            "char": DataType.CHAR,
            "string": DataType.STRING
        }
        return type_map.get(type_node.type_name.lower(), DataType.INTEGER)
    
    elif isinstance(type_node, ArrayTypeNode):
        return DataType.ARRAY
    
    elif isinstance(type_node, CustomTypeNode):
        return DataType.CUSTOM
    
    else:
        return DataType.INTEGER  # Default fallback


# Example usage and testing
if __name__ == "__main__":
    # Create symbol table
    st = SymbolTable()
    
    # Test basic operations
    print("=== Testing Symbol Table ===")
    
    # Add some variables
    st.enter_variable("x", DataType.INTEGER)
    st.enter_variable("y", DataType.REAL)
    st.enter_constant("PI", DataType.REAL, 3.14159)
    
    # Test lookup
    result = st.lookup("x")
    print(f"Lookup 'x': {result}")
    
    result = st.lookup("PI")
    print(f"Lookup 'PI': {result}")
    
    result = st.lookup("nonexistent")
    print(f"Lookup 'nonexistent': {result}")
    
    # Enter procedure scope
    proc_idx = st.enter_procedure("test_proc", DataType.VOID)
    st.enter_parameter("param1", DataType.INTEGER)
    st.enter_variable("local_var", DataType.BOOLEAN)
    
    # Test lookup in nested scope
    result = st.lookup("param1")
    print(f"Lookup 'param1' in procedure: {result}")
    
    result = st.lookup("x")  # Should find global x
    print(f"Lookup global 'x' from procedure: {result}")
    
    # Print entire table
    st.print_table()