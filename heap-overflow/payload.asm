bits 64
section .text

global _start
_start:
	sub rsp, byte 0x78
	xor rcx, rcx
	mov byte [rel pad], cl
	lea rdi, [rel path]
	mov qword [rsp+0x10], rdi
	mov qword [rsp+0x18], rcx
	mov qword [rsp+0x08], rcx
	lea rsi, [rsp+0x10]
	lea rdx, [rsp+0x08]
	mov rax, rcx
	mov al, byte 59
	syscall

section .data
path db '/bin/sh'
pad db 0x01
