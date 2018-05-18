extern printf
extern getaddrinfo
extern exit

global _start

struc addrinfo
        .ai_flags: resd 1
        .ai_family: resd 1
        .ai_socktype: resd 1
        .ai_addrlen: resd 1
        .ai_addr: resd 1
        .ai_canonname: resd 1
        .ai_next: resd 1
endstruc

section .data
        hints:
        istruc addrinfo
        at addrinfo.ai_flags, dd 0
        at addrinfo.ai_family, dd 2             ; AF_INET 2
        at addrinfo.ai_socktype, dd 0
        at addrinfo.ai_addrlen, dd 0
        at addrinfo.ai_addr, dd 0
        at addrinfo.ai_canonname, dd 0
        at addrinfo.ai_next, dd 0
        iend
        host: db "www.google.de", 0
        succ_msg: db "Success", 0xA, 0
        err_msg: db "Error", 0xA, 0

section .bss
        result: resd 1
        status: resd 1

section .text
_start:
        push result
        push hints
        push 0
        push host
        call getaddrinfo
        add esp, 10h

        cmp eax, 0
        jne err
        push succ_msg
        call printf
        add esp, 4
        jmp end
err:
        push err_msg
        call printf
        add esp, 4
end:
        push 0
        call exit
