BITS 32

extern dprintf
extern getaddrinfo
extern freeaddrinfo
extern gai_strerror
extern inet_ntop
extern exit

global _start

%define STDOUT_FILENO 1
%define STDERR_FILENO 2
%define EXIT_SUCCESS 0
%define EXIT_FAILURE 1
%define AF_INET 2
%define INET_ADDRSTRLEN 16

struc addrinfo
        .ai_flags: resd 1
        .ai_family: resd 1
        .ai_socktype: resd 1
        .ai_addrlen: resd 1
        .ai_addr: resd 1
        .ai_canonname: resd 1
        .ai_next: resd 1
endstruc

struc sockaddr_in
	.sin_family: resw 1
	.sin_port: resw 1
	.sin_addr: resd 1
	.sin_zero: resq	1
endstruc

struc in_addr
	.s_addr: resd 1
endstruc

section .data
        hints:
        istruc addrinfo
		at addrinfo.ai_flags, dd 0
		at addrinfo.ai_family, dd AF_INET
		at addrinfo.ai_socktype, dd 0
		at addrinfo.ai_addrlen, dd 0
		at addrinfo.ai_addr, dd 0
		at addrinfo.ai_canonname, dd 0
		at addrinfo.ai_next, dd 0
        iend
        msg_success: db "IPv4: %s", 0xA, 0
        msg_error: db "Error: %s", 0xA, 0
	msg_usage: db "Usage: %s <hostname>", 0xA, 0

section .bss
        result: resd 1
	ipv4_addr: resb INET_ADDRSTRLEN

section .text
_start:
	cmp esp, 2				; argc is at esp. Must be greater or equal 2, else print usage
	jge query
usage:
	lea eax, [esp+4]			; esp+4 is the address of argv[0]
	push eax
	push msg_usage
	push STDERR_FILENO
	call dprintf
	add esp, 0xC
	jmp exit_failure
query:
        push result
        push hints
        push 0
	lea eax, [esp+8]			; esp+8 is the address of argv[1] (hostname)
        push eax
        call getaddrinfo
        add esp, 0x10
        cmp eax, 0
        jne error
        push result
        call print_result
        add esp, 4
	push result
	call freeaddrinfo
	add esp, 4
        jmp exit_success
error:
	push eax				; return value of getaddrinfo
	call gai_strerror
	add esp, 4
	push eax				; return value of gai_strerror (char *)
        push msg_error
	push STDERR_FILENO
        call dprintf
        add esp, 0xC
exit_failure:
        push EXIT_FAILURE
        call exit
exit_success:
        push EXIT_SUCCESS
        call exit


print_result:
	sub esp, 0xC				; rp, addr
	mov esp, [ebx+4]			; rp = result
	mov esp+8, 0				; first = 0
.loop:
	cmp [esp], 0				; loop while rp != NULL
	je .end
	inc [esp+8]				; ++first
	cmp [esp+addrinfo.ai_family], AF_INET
	jne .next
	lea eax, esp+addrinfo.ai_addr		; load address of rp->ai_addr into eax
	mov esp+4, eax+sockaddr_in.sin_addr	; move address of sockaddr_in->sin_addr of rp in to addr
	push INET_ADDRSTRLEN
	push ipv4_addr
	push [esp+4]
	push AF_INET
	call inet_ntop
	add esp, 0x10
	jmp end
.next
	mov esp, [esp+addrinfo.ai_next]		; rp = rp->ai_next
.end
	mov esp, ebp
	pop ebp
	ret
