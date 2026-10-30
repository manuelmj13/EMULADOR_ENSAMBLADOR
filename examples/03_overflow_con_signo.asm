mov eax, 0x7FFFFFFF
add eax, 1
jo overflow_detectado
jmp fin
overflow_detectado:
mov ebx, 1
fin:
hlt
