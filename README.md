# Mini-emulador educativo x86 IA-32

Mini-emulador didáctico de un subconjunto mínimo de x86 IA-32 (32 bits,
sintaxis Intel). Permite visualizar paso a paso la ejecución de operaciones
aritméticas y saltos condicionales, junto con registros y flags.

## Requisitos

- Python 3.11 o superior
- `pytest` para ejecutar las pruebas
- `PyQt6` únicamente para la interfaz gráfica

Instalación para desarrollo:

```powershell
python -m pip install -e ".[dev]"
```

Para instalar también la GUI:

```powershell
python -m pip install -e ".[dev,gui]"
```

## Arquitectura

El motor está separado de la interfaz y sigue este pipeline:

```text
tokenizer -> parser -> evaluator -> executor
```

- `mini86/isa.py`: registros, flags e instrucciones soportadas.
- `mini86/tokens.py` y `mini86/tokenizer.py`: tokens del código fuente.
- `mini86/ast_nodes.py` y `mini86/parser.py`: AST y validación sintáctica.
- `mini86/machine.py`: registros, flags, `eip` y estado de la CPU.
- `mini86/evaluator.py`: operaciones ALU y condiciones de `jcc` puras.
- `mini86/executor.py`: ejecución paso a paso y snapshots.
- `ui/`: interfaz PyQt6; consume `Executor`, pero el motor no importa PyQt6.

## Ejecutar las pruebas

```powershell
pytest -q
```

## Usar la CLI

Ejecutar un programa hasta `hlt`:

```powershell
python -m mini86.cli examples\03_overflow_con_signo.asm --run
```

Mostrar cada instrucción ejecutada:

```powershell
python -m mini86.cli examples\03_overflow_con_signo.asm --step
```

También está disponible el comando instalado:

```powershell
mini86 examples\03_overflow_con_signo.asm --run
```

## Iniciar la GUI

```powershell
python -m ui.app
```

O, después de instalar el paquete:

```powershell
mini86-gui
```

La ventana incluye `Step`, `Run`, `Reset` y `Abrir .asm`. Muestra la línea
actual, los ocho registros, los cinco flags y la última comparación.

## ISA soportada

### Registros

`eax`, `ebx`, `ecx`, `edx`, `esi`, `edi`, `esp`, `ebp`.

Todos son registros completos de 32 bits; no hay subregistros.

### Flags

`CF` (carry), `ZF` (zero), `SF` (sign), `OF` (overflow) y `PF` (parity).

### Instrucciones

- Transferencia: `mov`
- Aritmética: `add`, `sub`, `inc`, `dec`
- Comparación: `cmp`, `test`
- Control: `jmp`, `hlt` y todos los `jcc` estándar:
  `je/jz`, `jne/jnz`, `jg/jnle`, `jge/jnl`, `jl/jnge`, `jle/jng`,
  `ja/jnbe`, `jae/jnb/jnc`, `jb/jnae/jc`, `jbe/jna`, `js`, `jns`,
  `jo`, `jno`

Se aceptan comentarios con `;`, etiquetas como `label:` y números decimales,
hexadecimales (`0x..` o `..h`) y binarios (`0b..` o `..b`).

## Fuera del alcance

El proyecto no implementa memoria, operandos como `[reg+off]`, `dword ptr`,
`lea`, subregistros de 8/16 bits, pila (`push`, `pop`, `call`, `ret`),
multiplicación o división, operaciones lógicas `and`/`or`/`xor`,
corrimientos, directivas `.data`/`.text`/`db`/`dw`/`dd` ni código máquina real.

## Ejemplo estrella: overflow con signo

El archivo [examples/03_overflow_con_signo.asm](examples/03_overflow_con_signo.asm)
ejecuta:

```asm
mov eax, 0x7FFFFFFF
add eax, 1
jo overflow_detectado
```

`0x7FFFFFFF` es `INT32_MAX`, el mayor entero signed de 32 bits. Al sumarle
uno, el resultado binario es `0x80000000`, que representa `INT32_MIN` en signed.
Por eso `OF=1`: el resultado signed salió del rango `-2147483648..2147483647`.

`SF=1` indica otra cosa: el bit más significativo del resultado es uno, por lo
que el resultado tiene signo negativo en la representación signed. En este
caso `SF` y `OF` coinciden en uno, pero no son el mismo concepto: uno describe
el bit de signo del resultado y el otro detecta desbordamiento signed.

`CF=0` porque no hubo carry fuera del bit 32: la suma unsigned
`0x7FFFFFFF + 1` es `0x80000000`, todavía representable como unsigned.
Por tanto, este caso no lo detectaría `CF`; se necesita `OF` y el salto `jo`.

## Ejemplos incluidos

- `01_salto_incondicional.asm`: `jmp`.
- `02_comparacion_basica.asm`: `cmp` y `je`.
- `03_overflow_con_signo.asm`: overflow signed y `jo`.
- `04_flag_de_carry.asm`: carry unsigned y `jc`.
- `05_inc_no_toca_carry.asm`: `inc` preserva `CF`.
- `06_loop_con_dec.asm`: bucle con `dec` y `jnz`.
- `07_test_vs_cmp.asm`: diferencia entre `test` y `cmp`.