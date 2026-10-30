; test aplica AND solo para actualizar flags; no escribe eax.
mov eax, 0b1010
test eax, 0b0010
jnz bit_encendido
mov ebx, 0
jmp fin
bit_encendido:
mov ebx, 1
fin:
hlt
