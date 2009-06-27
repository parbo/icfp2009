#include "math.h"
#include "stdio.h"
#include "stdint.h"
#include "stdlib.h"
#include "string.h"

/*              OPCODE Semantics                     Note */
/* Add r1 r2    0x1    rd ← mem[r1 ] + mem[r2 ] */
/* Sub r1 r2    0x2    rd ← mem[r1 ] - mem[r2 ] */
/* Mult r1 r2   0x3    rd ← mem[r1 ] * mem[r2 ] */
/* Div r1 r2    0x4    if mem[r2 ] = 0.0 */
/*                     then rd ← 0.0 */
/*                     else rd ← mem[r1 ] / mem[r2 ] */
/* Output r1 r2 0x5    port[r1 ] ← mem[r2 ] */
/* Phi r1 r2    0x6    if status = ’1’ */
/*                     then rd ←mem[r1 ] */
/*                     else rd ←mem[r2 ] */

typedef enum _D_opcodes
{
	D_OP_ADD = 0x1,
	D_OP_SUB = 0x2,
	D_OP_MULT = 0x3,
	D_OP_DIV = 0x4,
	D_OP_OUTPUT = 0x5,
	D_OP_PHI = 0x6
} D_opcodes;

/*   struction OPCODE Semantics               Note */
/* Noop        0x0    rd ← mem[rd ] */
/* Cmpz imm r1 0x1    status← mem[r1 ] op 0.0 a */
/* Sqrt r1     0x2    rd ← | mem[r1 ]| */
/* Copy r1     0x3    rd ← mem[r1 ] */
/* Input r1    0x4    rd ← port[r1 ] */

typedef enum _S_opcodes
{
	S_OP_NOOP = 0x0,
	S_OP_CMPZ = 0x1,
	S_OP_SQRT = 0x2,
	S_OP_COPY = 0x3,
	S_OP_INPUT = 0x4
} S_opcodes;

/* OPCODE Encoding Operation */
/* LTZ    0x0      < */
/* LEZ    0x1      ≤ */
/* EQZ    0x2      = */
/* GEZ    0x3      ≥ */
/*        0x4 */
/* GTZ             > */

typedef enum _CMPZ_opcodes
{
	CMPZ_OP_LTZ = 0x0,
	CMPZ_OP_LEZ = 0x1,
	CMPZ_OP_EQZ = 0x2,
	CMPZ_OP_GEZ = 0x3,
	CMPZ_OP_GTZ = 0x4
} CPMZ_opcodes;

#define ADDRSPACESZ 16384

#define TRACE(LVL, x) if (LVL <= g_dbglvl) printf x
#define TRACE0(x) TRACE(0, x)
#define TRACE1(x) TRACE(1, x)
#define TRACE2(x) TRACE(2, x)
#define TRACE3(x) TRACE(3, x)

uint32_t g_status = 0;
double g_data[ADDRSPACESZ];
uint32_t g_instructions[ADDRSPACESZ];
double g_input[ADDRSPACESZ];
double g_output[ADDRSPACESZ];

int g_dbglvl = 0;

void debuglevel(int lvl)
{
    g_dbglvl = lvl;
}

void init()
{
    uint32_t i = 0;
    g_status = 0;
    for (i = 0; i < ADDRSPACESZ; ++i)
    {
        g_data[i] = 0.0;
        g_instructions[i] = 0u;
        g_input[i] = 0.0;
        g_output[i] = 0.0;
    }
}

void load(const char* filename)
{
    FILE* f = fopen(filename, "rb");
    char frame[12];
    uint32_t addr = 0;
    TRACE1(("Loading: %s\n", filename));
    TRACE1(("double size: %d\n", sizeof(double)));
    if (f)
    {
        while (fread(frame, sizeof(frame), 1, f))
        {
            if (addr >= 0 && addr < ADDRSPACESZ)
            {
                uint32_t ins;
                double data;
                if (addr % 2 == 0)
                {
                    // even
                    memcpy(&data, &frame[0], 8);
                    memcpy(&ins, &frame[8], 4);
                }
                else
                {
                    // odd
                    memcpy(&ins, &frame[0], 4);
                    memcpy(&data, &frame[4], 8);
                }
                g_data[addr] = data;
                g_instructions[addr] = ins;
                ++addr;
            }
            else
            {
                TRACE1(("Error: binary exceeds address space\n"));
                break;
            }
        }
        TRACE1(("EOF, read %d\n", addr));
        fclose(f);
    }    
}

void writeinput(uint32_t port, double val)
{
    if (port >= 0 && port < ADDRSPACESZ)
    {
        g_input[port] = val;
    }
    else
    {
        TRACE1(("Error: port outside of range %d\n", port));
    }
}

double readinput(uint32_t port)
{
    double retval = 0.0;
    if (port >= 0 && port < ADDRSPACESZ)
    {
        retval = g_input[port];
    }
    else
    {
        TRACE1(("Error: port outside of range %d\n", port));
    }    
    return retval;
}

double readoutput(uint32_t port)
{
    double retval = 0.0;
    if (port >= 0 && port < ADDRSPACESZ)
    {
        retval = g_output[port];
    }
    else
    {
        TRACE1(("Error: port outside of range %d\n", port));
    }    
    return retval;
}

void timestep()
{
    uint32_t pc = 0;
    for (pc = 0; pc < ADDRSPACESZ; ++pc)
    {
        uint32_t ins = g_instructions[pc];
        uint32_t op = ins >> 28;
        if (op)
        {
            // D-type instruction
            uint32_t r1 = (ins >> 14) & 0x3fff;
            uint32_t r2 = ins & 0x3fff;            
            switch (op)
            {
                case D_OP_ADD:
                    g_data[pc] = g_data[r1] + g_data[r2];
                    TRACE3(("%d D: ADD, %d, %d, %f, %f, %f\n", pc, r1, r2, g_data[r1], g_data[r2], g_data[pc]));
                    break;
                case D_OP_SUB:
                    g_data[pc] = g_data[r1] - g_data[r2];
                    TRACE3(("%d D: SUB, %d, %d, %f, %f, %f\n", pc, r1, r2, g_data[r1], g_data[r2], g_data[pc]));
                    break;
                case D_OP_MULT:
                    g_data[pc] = g_data[r1] * g_data[r2];
                    TRACE3(("%d D: MULT, %d, %d, %f, %f, %f\n", pc, r1, r2, g_data[r1], g_data[r2], g_data[pc]));
                    break;
                case D_OP_DIV:
                    if (g_data[r2] == 0.0)
                    {
                        g_data[pc] = 0.0;
                    }
                    else
                    {
                        g_data[pc] = g_data[r1] / g_data[r2];
                    }
                    TRACE3(("%d D: DIV, %d, %d, %f, %f, %f\n", pc, r1, r2, g_data[r1], g_data[r2], g_data[pc]));
                    break;
                case D_OP_OUTPUT:
                    g_output[r1] = g_data[r2];
                    TRACE3(("%d D: OUTPUT, %d, %d, %f, %f, %f\n", pc, r1, r2, g_data[r1], g_data[r2], g_output[r1]));
                    break;
                case D_OP_PHI:
                    g_data[pc] = g_status ? g_data[r1] : g_data[r2];
                    TRACE3(("%d D: PHI, %d, %d, %f, %f, %f, %d\n", pc, r1, r2, g_data[r1], g_data[r2], g_data[pc], g_status));
                    break;
                default:
                    TRACE1(("Error: invalid OP %d\n", op));
            }
        }
        else
        {
            // S-type instruction
            uint32_t imm = (ins >> 21) & 0x7;
            uint32_t r1 = ins & 0x3fff;
            op = (ins >> 24) & 0xf;
            switch (op)
            {
                case S_OP_NOOP:
                    TRACE3(("%d S: NOOP, %d, %d, %f, %f\n", pc, imm, r1, g_data[r1], g_data[pc]));
                    break;
                case S_OP_CMPZ:
                    {
                        switch (imm)
                        {
                            case CMPZ_OP_LTZ:
                                g_status = (g_data[r1] < 0.0) ? 1 : 0;
                                TRACE3(("%d S: CMPZ <, %d, %d, %f, %f, %d\n", pc, imm, r1, g_data[r1], g_data[pc], g_status));
                                break;
                            case CMPZ_OP_LEZ:
                                g_status = (g_data[r1] <= 0.0) ? 1 : 0;
                                TRACE3(("%d S: CMPZ <=, %d, %d, %f, %f, %d\n", pc, imm, r1, g_data[r1], g_data[pc], g_status));
                                break;
                            case CMPZ_OP_EQZ:
                                g_status = (g_data[r1] == 0.0) ? 1 : 0;
                                TRACE3(("%d S: CMPZ ==, %d, %d, %f, %f, %d\n", pc, imm, r1, g_data[r1], g_data[pc], g_status));
                                break;
                            case CMPZ_OP_GEZ:
                                g_status = (g_data[r1] >= 0.0) ? 1 : 0;
                                TRACE3(("%d S: CMPZ >=, %d, %d, %f, %f, %d\n", pc, imm, r1, g_data[r1], g_data[pc], g_status));
                                break;
                            case CMPZ_OP_GTZ:
                                g_status = (g_data[r1] > 0.0) ? 1 : 0;
                                TRACE3(("%d S: CMPZ >, %d, %d, %f, %f, %d\n", pc, imm, r1, g_data[r1], g_data[pc], g_status));
                                break;
                            default:
                                TRACE1(("Error: invalid CMPZ OP %d\n", imm));
                        }
                    }
                    break;
                case S_OP_SQRT:
                    g_data[pc] = abs(sqrt(g_data[r1]));
                    TRACE3(("%d S: SQRT, %d, %d, %f, %f\n", pc, imm, r1, g_data[r1], g_data[pc]));
                    break;
                case S_OP_COPY:
                    g_data[pc] = g_data[r1];
                    TRACE3(("%d S: COPY, %d, %d, %f, %f\n", pc, imm, r1, g_data[r1], g_data[pc]));
                    break;
                case S_OP_INPUT:
                    g_data[pc] = g_input[r1];
                    TRACE3(("%d S: INPUT, %d, %d, %f, %f\n", pc, imm, r1, g_data[r1], g_data[pc]));
                    break;
                default:
                    TRACE1(("Error: invalid OP %d\n", op));
            }
        }
    }
}
