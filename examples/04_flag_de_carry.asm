; La suma unsigned supera 32 bits y activa CF.
mov eax, 0xFFFFFFFF
add eax, 1
jc carry_detectado
jmp fin
carry_detectado:
mov ebx, 1
fin:
hlt
