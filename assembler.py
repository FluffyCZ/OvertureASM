REGISTERS = {
    "r0": 0b000, "r1": 0b001, "r2": 0b010, "r3": 0b011,
    "r4": 0b100, "r5": 0b101, "in": 0b110, "out": 0b110
}

def assemble(asm_code):
    lines = asm_code.strip().split("\n")

    labels = {}
    clean_instructions = []
    pc = 0  
    
    for raw_line in lines:
        line = raw_line.split(";")[0].strip()
        if not line:
            continue
            
        if line.endswith(":"):
            label_name = line[:-1].strip().lower()
            labels[label_name] = pc
            continue
            
        clean_instructions.append((pc, line))
        pc += 1  # Every instruction has 1 byte

    binary_output = bytearray()
    
    for pc, line in clean_instructions:
        tokens = [t.strip(",%") for t in line.replace(",", " ").split()]
        if not tokens:
            continue
            
        mnemonic = tokens[0].lower()
        args = tokens[1:]
        
        byte = 0
        
        if mnemonic == "mov":
            if len(args) != 2:
                raise SyntaxError(f"Instruction 'mov' is expecting 2 arguments: {line}")
            dest = REGISTERS[args[0].lower()]
            src = REGISTERS[args[1].lower()]
            byte = (0b10 << 6) | ((dest & 0b111) << 3) | (src & 0b111)
            
        elif mnemonic == "imm":
            if len(args) != 1:
                raise SyntaxError(f"Instruction 'imm' is expecting 1 argument: {line}")
            
            val_str = args[0]
            if val_str.lower() in labels:
                val = labels[val_str.lower()]
            else:
                val = int(val_str, 0)
                
            if not (0 <= val <= 63):
                raise ValueError(f"The value for 'imm' has to be in range 0-63 (6 bits): {val}")
                
            byte = (0b00 << 6) | (val & 0x3F)
            
        elif mnemonic in ("nand", "or", "and", "nor", "add", "sub"):
            opcodes = {
                "nand": 0b01000000, "or":   0b01000001,
                "and":  0b01000010, "nor":  0b01000011,
                "add":  0b01000100, "sub":  0b01000101
            }
            byte = opcodes[mnemonic]
            
        elif mnemonic in ("nop", "jmp", "jz", "jnz", "jl", "jge", "jle", "jg"):
            opcodes = {
                "nop": 0b11000000, "jmp": 0b11000001,
                "jz":  0b11000010, "jnz": 0b11000011,
                "jl":  0b11000100, "jge": 0b11000101,
                "jle": 0b11000110, "jg":  0b11000111
            }
            byte = opcodes[mnemonic]
        else:
            raise ValueError(f"Unknown instruction: {mnemonic}")
            
        binary_output.append(byte)

    return binary_output