; INT32_MAX + 1 produce INT32_MIN: OF=1 y SF=1, pero CF=0.
mov eax, 0x7FFFFFFF
add eax, 1
jo overflow_detectado
jmp fin
overflow_detectado:
mov ebx, 1
fin:
hlt
