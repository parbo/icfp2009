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


typedef enum _OP_opcodes
{
	OP_NOOP = 0x0,
	OP_ADD = 0x1,
	OP_SUB = 0x2,
	OP_MULT = 0x3,
	OP_DIV = 0x4,
	OP_OUTPUT = 0x5,
	OP_PHI = 0x6,
	OP_CMPZ_LTZ = 0x7,
	OP_CMPZ_LEZ = 0x8,
	OP_CMPZ_EQZ = 0x9,
	OP_CMPZ_GEZ = 0xa,
	OP_CMPZ_GTZ = 0xb,
	OP_SQRT = 0xc,
	OP_COPY = 0xd,
	OP_INPUT = 0xe
} OP_opcodes;


#define ADDRSPACESZ 16384

#define TRACE(LVL, x) if (LVL <= g_dbglvl) printf x
//#define TRACE(LVL, x)
#define TRACE0(x) TRACE(0, x)
#define TRACE1(x) TRACE(1, x)
#define TRACE2(x) TRACE(2, x)
#define TRACE3(x) TRACE(3, x)

typedef struct _frame_t
{
	double data;
	OP_opcodes op;
	uint16_t r1;
	uint16_t r2;
} frame_t;

uint32_t g_status = 0;

frame_t g_frames[ADDRSPACESZ];
double g_input[ADDRSPACESZ];
double g_output[ADDRSPACESZ];

uint32_t g_lastvalid = 0;

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
        g_frames[i].data = 0.0;
        g_frames[i].op = OP_NOOP;
        g_frames[i].r1 = 0u;
		g_frames[i].r2 = 0u;
		
        g_input[i] = 0.0;
        g_output[i] = 0.0;
		g_lastvalid = 0;
    }
}

frame_t getframe(double data, uint32_t ins)
{
	uint32_t op = ins >> 28;
	if (op)
	{
		// D-type instruction
		frame_t f;
		f.op = OP_NOOP;
		f.r1 = (ins >> 14) & 0x3fff;
		f.r2 = ins & 0x3fff;            
		f.data = data;
		switch (op)
		{
		case D_OP_ADD:
			f.op = OP_ADD;
			break;
		case D_OP_SUB:
			f.op = OP_SUB;
			break;
		case D_OP_MULT:
			f.op = OP_MULT;
			break;
		case D_OP_DIV:
			f.op = OP_DIV;
			break;
		case D_OP_OUTPUT:
			f.op = OP_OUTPUT;
			break;
		case D_OP_PHI:
			f.op = OP_PHI;
			break;
		}
		return f;
	}
	else
	{
		// S-type instruction
		uint32_t imm = (ins >> 21) & 0x7;
        frame_t f;
		f.data = data;
		f.op = OP_NOOP;
		f.r1 = ins & 0x3fff;
		f.r2 = 0;
		op = (ins >> 24) & 0xf;
		switch (op)
		{
		case S_OP_NOOP:
			f.op = OP_NOOP;
			break;
		case S_OP_CMPZ:
			switch (imm)
			{
			case CMPZ_OP_LTZ:
				f.op = OP_CMPZ_LTZ;
				break;
			case CMPZ_OP_LEZ:
				f.op = OP_CMPZ_LEZ;
				break;
			case CMPZ_OP_EQZ:
				f.op = OP_CMPZ_EQZ;
				break;
			case CMPZ_OP_GEZ:
				f.op = OP_CMPZ_GEZ;
				break;
			case CMPZ_OP_GTZ:
				f.op = OP_CMPZ_GTZ;
				break;
			}
			break;
		case S_OP_SQRT:
			f.op = OP_SQRT;
			break;
		case S_OP_COPY:
			f.op = OP_COPY;
			break;
		case S_OP_INPUT:
			f.op = OP_INPUT;
			break;
		}
		return f;
	}
}

int load(const char* filename)
{
    FILE* f = fopen(filename, "rb");
    char frame[12];
    uint32_t addr = 0;
    uint32_t ret = 0;
    TRACE1(("Loading: %s\n", filename));
    TRACE1(("double size: %d\n", sizeof(double)));
    if (f)
    {
        ret = 1;
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
                g_frames[addr] = getframe(data, ins);
				if (g_frames[addr].op != OP_NOOP || data != 0.0)
				{
					g_lastvalid = addr;
				}
                ++addr;
            }
            else
            {
                TRACE1(("Error: binary exceeds address space\n"));
                ret = 0;
                break;
            }
        }
        TRACE1(("EOF, read %d\n", addr));
        fclose(f);
    }    
	TRACE1(("%d valid instructions", g_lastvalid));
    return ret;
}

void writeinput(uint32_t port, double val)
{
    if (port >= 0 && port < ADDRSPACESZ)
    {
        if (val != g_input[port])
        {
            TRACE1(("write port: %d, val %.20f\n", port, val));
        }
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
    for (pc = 0; pc <= g_lastvalid; ++pc)
    {
        frame_t* f = &g_frames[pc];
		switch (f->op)
		{
		case OP_NOOP:
			break;
		case OP_ADD:
			f->data = g_frames[f->r1].data + g_frames[f->r2].data;
			break;
		case OP_SUB:
			f->data = g_frames[f->r1].data - g_frames[f->r2].data;
			break;
		case OP_MULT:
			f->data = g_frames[f->r1].data * g_frames[f->r2].data;
			break;
		case OP_DIV:
			if (g_frames[f->r2].data == 0.0)
			{
				f->data = 0.0;
			}
			else
			{
				f->data = g_frames[f->r1].data / g_frames[f->r2].data;
			}
			break;
		case OP_OUTPUT:
			g_output[f->r1] = g_frames[f->r2].data;
			break;
		case OP_PHI:
			f->data = g_status ? g_frames[f->r1].data : g_frames[f->r2].data;
			break;
		case OP_CMPZ_LTZ:
			g_status = g_frames[f->r1].data < 0.0 ? 1 : 0;
			break;
		case OP_CMPZ_LEZ:
			g_status = g_frames[f->r1].data <= 0.0 ? 1 : 0;
			break;
		case OP_CMPZ_EQZ:
			g_status = g_frames[f->r1].data == 0.0 ? 1 : 0;
			break;
		case OP_CMPZ_GEZ:
			g_status = g_frames[f->r1].data >= 0.0 ? 1 : 0;
			break;
		case OP_CMPZ_GTZ:
			g_status = g_frames[f->r1].data > 0.0 ? 1 : 0;
			break;
		case OP_SQRT:
			f->data = sqrt(g_frames[f->r1].data);
			break;
		case OP_COPY:
			f->data = g_frames[f->r1].data;
			break;
		case OP_INPUT:
			f->data = g_input[f->r1];
			break;
		default:
			TRACE1(("Error: invalid OP %d\n", f->op));
		}
    }
}
