gethostip: gethostip.c
	gcc -o gethostip gethostip.c

gethostip_asm: gethostip_asm.o
	gcc -m32 -o gethostip_asm gethostip_asm.o
	rm -f gethostip_asm.o

gethostip_asm.o: gethostip.asm
	nasm -f elf -g gethostip.asm -o gethostip_asm.o

clean:
	rm -f gethostip
	rm -f gethostip_asm
