BITS 32

extern dprintf
extern getaddrinfo
extern freeaddrinfo
extern gai_strerror
extern inet_ntop
extern exit

global main

;------------------------------------------------------
; Defines
;------------------------------------------------------

%define STDOUT_FILENO 1
%define STDERR_FILENO 2
%define EXIT_SUCCESS 0
%define EXIT_FAILURE 1
; defined in sys/socket.h (bits/socket.h)
%define AF_UNSPEC 0
%define AF_INET 2
%define AF_INET6 10
; defined in netinet/in.h
%define INET_ADDRSTRLEN 16
%define INET6_ADDRSTRLEN 46
%define NARGS 2

struc addrinfo
	.ai_flags: resd 1
	.ai_family: resd 1
	.ai_socktype: resd 1
	.ai_protocol: resd 1
	.ai_addrlen: resd 1
	.ai_addr: resd 1
	.ai_canonname: resd 1
	.ai_next: resd 1
endstruc

struc in_addr
	.s_addr: resd 1
endstruc

struc in6_addr
	.s_addr: resb 16
endstruc

struc sockaddr_in
	.sin_family: resw 1
	.sin_port: resw 1
	.sin_addr: resb in_addr_size
	.sin_zero: resq	1
endstruc

struc sockaddr_in6
	.sin6_family: resw 1
	.sin6_port: resw 1
	.sin6_flowinfo: resd 1
	.sin6_addr: resb in6_addr_size
	.sin6_scope_id: resd 1
endstruc

;------------------------------------------------------
; Section DATA
;------------------------------------------------------

section .data
	first: dd 0
	first6: dd 0
	hints:
		istruc addrinfo
		at addrinfo.ai_flags, dd 0
		at addrinfo.ai_family, dd AF_UNSPEC
		at addrinfo.ai_socktype, dd 0
		at addrinfo.ai_addrlen, dd 0
		at addrinfo.ai_addr, dd 0
		at addrinfo.ai_canonname, dd 0
		at addrinfo.ai_next, dd 0
		iend
	msg_usage: db "Usage: %s <hostname>", 0xA, 0
	msg_error: db "Error: %s", 0xA, 0
	msg_ipv4: db "IPv4: %s", 0xA, 0
	msg_ipv6: db "IPv6: %s", 0xA, 0
; TODO remove when finished
	dbg1: db "ipv4", 0xA, 0
	dbg2: db "ipv6", 0xA, 0

;------------------------------------------------------
; Section BSS
;------------------------------------------------------

section .bss
	result: resd 1

;------------------------------------------------------
; Section TEXT
;------------------------------------------------------

section .text
main:
; Check if the command line arguments are present
	mov ebx, DWORD [esp+4]		; move argc into ebx
	cmp DWORD ebx, NARGS		; compare argc with required argument count
	je .lookup
; Print usage
.usage:
	mov eax, DWORD [esp+8]		; load argv (char **) into eax
	mov ebx, DWORD [eax]		; dereference argv to get argv[0] (char *) and move it into ebx
	push ebx					; argv[0] is the address of the program name
	push msg_usage				; push the formatstring
	push DWORD STDERR_FILENO
	call dprintf
	add esp, 0xC				
	push EXIT_FAILURE
	call exit
; Do IP lookup for the hostname
.lookup:
	mov eax, DWORD [esp+8]		; load argv (char **) into eax
	mov ebx, DWORD [eax+4]		; move address of argv[1] (hostname) into ebx
	push DWORD result
	push DWORD hints
	push DWORD 0
	push ebx
	call getaddrinfo
	add esp, 0x10				; cleanup arguments
	cmp eax, DWORD 0			; check return value of getaddrinfo for error
	jne .error_getaddrinfo
	push DWORD [result]
	call print_result			; upon success print the result
	add esp, 4
	push DWORD [result]
	call freeaddrinfo
	add esp, 4
	push EXIT_SUCCESS
	call exit
.error_getaddrinfo:
	push eax					; push getaddrinfo error code
	call gai_strerror			; get string representation of error code
	add esp, 4
	push eax					; push error string returned by gai_strerror
	push msg_error
	push STDERR_FILENO
	call dprintf				; print error string
	add esp, 0xC
	push EXIT_FAILURE
	call exit

print_result:
; esp+0: rp
; esp+0x4: addr
; esp+0x8: addr6
; esp+0xC: ipv4_addr
; esp+0x10: ipv6_addr
	sub esp, 0x4c									; Allocate space for rp (4 Bytes), addr (4), addr6 (4), ipv4_addr (16), ipv6_addr (46) = 74 -> 76 (0x4c) for 4 byte alignment
	mov ebx, [esp+0x50]								; grep function arg 'result' (consider return address)
	mov [esp], ebx									; esp+0: rp = result
.loop:
	cmp [esp], DWORD 0								; loop while rp != NULL
	jz .end
	mov ebx, [ebx+addrinfo.ai_family]				; move family into ebx
	cmp ebx, DWORD AF_INET							; check if its an IPv4 address
	je .ipv4
	cmp ebx, DWORD AF_INET6							; check if its an IPv6 address
	je .ipv6
.loop_update:
	mov ebx, [esp]
	mov ebx, [ebx+addrinfo.ai_next]
	mov [esp], ebx									; rp = rp->ai_next
	jmp .loop
.ipv4:
	inc DWORD [first]
	cmp [first], DWORD 1
	jne .loop_update								; If IPv4 was already printed continue

; TODO do printing here
; print some info so we know we got here
	push dbg1
	push DWORD STDOUT_FILENO
	call dprintf
	add esp, 0x8

	jmp .loop_update
.ipv6:
	inc DWORD [first6]
	cmp [first6], DWORD 1
	jne .loop_update								; If IPv6 was already printed continue
; TODO not working
	mov ebx, [esp]									; get address of addrinfo struct
	mov ebx, [ebx+addrinfo.ai_addr]					; get address of IP struct
	lea ebx, [ebx+sockaddr_in6.sin6_addr]			; get address of IPv6 address bytes
	mov [esp+0x8], ebx								; save it on stack esp+8: addr6
	lea ecx, [esp+0x10]								; addr of ipv6_addr
	push DWORD INET6_ADDRSTRLEN
	push ecx
	push ebx
	push DWORD AF_INET6
	call inet_ntop
	add esp, 0x10

	mov ebx, [esp+0x10]
	push ebx
	push msg_ipv6
	push DWORD STDOUT_FILENO
	call dprintf
	add esp, 0xC
	jmp .loop_update
.end:
	add esp, 0x4c
	ret



