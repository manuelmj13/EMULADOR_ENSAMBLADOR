; dec reduce el contador sin modificar CF; jnz repite mientras no haya ZF.
mov ecx, 3
mov eax, 0
loop:
inc eax
dec ecx
jnz loop
hlt
