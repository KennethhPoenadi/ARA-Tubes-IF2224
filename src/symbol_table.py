
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

sys.path.insert(0, os.path.dirname(__file__))

from ast_nodes import (
    ASTNode, ProgramNode, VarDeclNode, ConstDeclNode, TypeDeclNode,
    ProcedureDeclNode, FunctionDeclNode, PrimitiveTypeNode, ArrayTypeNode,
    CustomTypeNode, RangeTypeNode, TypeSpecNode
)

class ObjectType(Enum):
    CONSTANT = "constant"
    VARIABLE = "variable" 
    TYPE = "type"
    PROCEDURE = "procedure"
    FUNCTION = "function"
    PROGRAM = "program"
    PARAMETER = "parameter"

class DataType(Enum):
    VOID = 0
    INTEGER = 1
    REAL = 2
    BOOLEAN = 3
    CHAR = 4
    ARRAY = 5
    STRING = 6
    CUSTOM = 6

class SymbolTableEntry:
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
    RESERVED_COUNT = 32
    
    def __init__(self):
        self.tab: List[Optional[SymbolTableEntry]] = []
        self.btab: List[BlockTableEntry] = []
        self.atab: List[ArrayTableEntry] = []
        
        self.current_level = 0
        self.current_block = -1
        self.next_address = 0
        self.display: List[int] = []
        
        self.RESERVED_WORDS = [
            "program", "variabel", "mulai", "selesai", "jika", 
            "maka", "selain-itu", "selama", "lakukan", "untuk",
            "ke", "turun-ke", "integer", "real", "boolean",
            "char", "larik", "dari", "prosedur", "fungsi",
            "konstanta", "tipe", "string", "kasus", "ulangi",
            "sampai", "rekaman",
            "dan", "atau", "tidak",
            "bagi", "mod"
        ]
        
        self._initialize_reserved_entries()
        self._initialize_builtins()
    
    def _initialize_reserved_entries(self):
        for i, word in enumerate(self.RESERVED_WORDS):
            entry = SymbolTableEntry(
                id=word,
                obj=ObjectType.TYPE,  
                type=DataType.VOID,
                ref=-1,
                nrm=True,
                lev=0,
                adr=0,
                link=-1
            )
            self.tab.append(entry)
    
    def _initialize_builtins(self):
        self.enter_block()
    
    def enter_block(self) -> int:
        block_entry = BlockTableEntry()
        self.btab.append(block_entry)
        block_index = len(self.btab) - 1
        
        if len(self.display) <= self.current_level:
            self.display.extend([-1] * (self.current_level - len(self.display) + 1))
        self.display[self.current_level] = len(self.tab)
        
        self.current_block = block_index
        return block_index
    
    def exit_block(self):
        if self.current_block >= 0:
            current_block_entry = self.btab[self.current_block]
            if len(self.tab) > 0:
                current_block_entry.last = len(self.tab) - 1
        
        if self.current_level > 0:
            self.current_level -= 1
        
        self.current_block = -1
        for i in range(len(self.btab) - 2, -1, -1):
            if i < len(self.btab) - 1:
                self.current_block = i
                break
    
    def enter_scope(self) -> int:
        return self.enter_block()
    
    def exit_scope(self):
        self.exit_block()
    
    def enter_procedure(self, name: str, return_type: DataType, level: int = None) -> int:
        if level is None:
            level = self.current_level
        
        self.current_level += 1
        block_index = self.enter_block()
        
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
        tab_index = len(self.tab) - 1
        
        if self.current_block >= 0:
            self.btab[self.current_block].last = tab_index
            self.btab[self.current_block].vsize += self._get_type_size(data_type, array_ref)
        self.next_address += self._get_type_size(data_type, array_ref)
        return tab_index
    
    def enter_program(self, name: str) -> int:
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
        tab_index = len(self.tab) - 1
        
        if self.current_block >= 0:
            self.btab[self.current_block].last = tab_index
        return tab_index
    
    def enter_constant(self, name: str, data_type: DataType, value: Any) -> int:
        entry = SymbolTableEntry(
            id=name,
            obj=ObjectType.CONSTANT,
            type=data_type,
            ref=0,
            lev=self.current_level,
            adr=0,
            link=self._get_current_scope_link()
        )
        self.tab.append(entry)
        tab_index = len(self.tab) - 1
        
        if self.current_block >= 0:
            self.btab[self.current_block].last = tab_index
        return tab_index
    
    def enter_type(self, name: str, type_def: DataType, ref: int = -1) -> int:
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
        tab_index = len(self.tab) - 1
        
        if self.current_block >= 0:
            self.btab[self.current_block].last = tab_index
        return tab_index
    
    def enter_parameter(self, name: str, data_type: DataType, by_reference: bool = False) -> int:
        entry = SymbolTableEntry(
            id=name,
            obj=ObjectType.PARAMETER,
            type=data_type,
            nrm=not by_reference,
            lev=self.current_level,
            adr=self.next_address,
            link=self._get_current_scope_link()
        )
        self.tab.append(entry)
        tab_index = len(self.tab) - 1
        self.next_address += self._get_type_size(data_type)
        
        if self.current_block >= 0:
            self.btab[self.current_block].lastpar = tab_index
            self.btab[self.current_block].last = tab_index
            self.btab[self.current_block].psize += self._get_type_size(data_type)
        return tab_index
    
    def enter_array(self, index_type: DataType, element_type: DataType,
                   low: int, high: int, element_ref: int = -1) -> int:
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
        if len(self.tab) == 0:
            return None
        
        current_scope_start = self.RESERVED_COUNT
        if (self.current_level < len(self.display) and 
            self.display[self.current_level] >= 0):
            current_scope_start = max(self.RESERVED_COUNT, self.display[self.current_level])
        
        for i in range(len(self.tab) - 1, self.RESERVED_COUNT - 1, -1):
            entry = self.tab[i]
            if entry is None:
                continue
            if entry.id == name:
                if entry.lev <= self.current_level:
                    return entry
        return None
    
    def lookup_with_index(self, name: str) -> tuple:
        if len(self.tab) == 0:
            return (None, -1)
        
        for i in range(len(self.tab) - 1, self.RESERVED_COUNT - 1, -1):
            entry = self.tab[i]
            if entry is None:
                continue
            if entry.id == name:
                if entry.lev <= self.current_level:
                    return (entry, i)
        return (None, -1)
    
    def lookup_in_current_scope(self, name: str) -> Optional[SymbolTableEntry]:
        current_scope_start = self.RESERVED_COUNT
        if (self.current_level < len(self.display) and 
            self.display[self.current_level] >= 0):
            current_scope_start = max(self.RESERVED_COUNT, self.display[self.current_level])
        
        for i in range(len(self.tab) - 1, current_scope_start - 1, -1):
            entry = self.tab[i]
            if entry is None:
                continue
            if entry.id == name and entry.lev == self.current_level:
                return entry
        return None
    
    def _get_current_scope_link(self) -> int:
        if len(self.tab) <= self.RESERVED_COUNT:
            return -1
        
        for i in range(len(self.tab) - 1, self.RESERVED_COUNT - 1, -1):
            entry = self.tab[i]
            if entry is None:
                continue
            if entry.lev == self.current_level:
                return i
        return -1
    
    def _get_type_size(self, data_type: DataType, array_ref: int = -1) -> int:
        if data_type == DataType.ARRAY and array_ref >= 0 and array_ref < len(self.atab):
            return self.atab[array_ref].size
        elif data_type in [DataType.INTEGER, DataType.BOOLEAN]:
            return 1
        elif data_type == DataType.REAL:
            return 2
        elif data_type == DataType.CHAR:
            return 1
        elif data_type == DataType.STRING:
            return 4
        else:
            return 1
    
    def get_symbol_info(self, index: int) -> Optional[SymbolTableEntry]:
        if 0 <= index < len(self.tab):
            return self.tab[index]
        return None
    
    def get_array_info(self, index: int) -> Optional[ArrayTableEntry]:
        if 0 <= index < len(self.atab):
            return self.atab[index]
        return None
    
    def get_block_info(self, index: int) -> Optional[BlockTableEntry]:
        if 0 <= index < len(self.btab):
            return self.btab[index]
        return None
    
    def print_table(self, table_name: str = "all"):
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
        return DataType.INTEGER

if __name__ == "__main__":
    st = SymbolTable()
    
    print("=== Testing Symbol Table ===")
    
    st.enter_variable("x", DataType.INTEGER)
    st.enter_variable("y", DataType.REAL)
    st.enter_constant("PI", DataType.REAL, 3.14159)
    
    result = st.lookup("x")
    print(f"Lookup 'x': {result}")
    
    result = st.lookup("PI")
    print(f"Lookup 'PI': {result}")
    
    result = st.lookup("nonexistent")
    print(f"Lookup 'nonexistent': {result}")
    
    proc_idx = st.enter_procedure("test_proc", DataType.VOID)
    st.enter_parameter("param1", DataType.INTEGER)
    st.enter_variable("local_var", DataType.BOOLEAN)
    
    result = st.lookup("param1")
    print(f"Lookup 'param1' in procedure: {result}")
    
    result = st.lookup("x")
    print(f"Lookup global 'x' from procedure: {result}")
    
    st.print_table()