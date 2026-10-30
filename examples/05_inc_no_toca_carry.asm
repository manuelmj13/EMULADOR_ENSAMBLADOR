; inc modifica ZF/SF/OF/PF, pero conserva el CF activado por add.
mov eax, 0xFFFFFFFF
add eax, 1
inc eax
jc carry_preservado
jmp fin
carry_preservado:
mov ebx, 1
fin:
hlt
