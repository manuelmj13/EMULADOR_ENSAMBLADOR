mov ecx, 3
mov eax, 0
loop:
inc eax
dec ecx
jnz loop
hlt
