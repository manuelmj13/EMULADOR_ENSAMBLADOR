; cmp actualiza ZF; je salta cuando ambos valores son iguales.
mov eax, 10
cmp eax, 10
je iguales
mov ebx, 0
jmp fin
iguales:
mov ebx, 1
fin:
hlt
