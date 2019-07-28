hostip: hostip.c
	gcc -o hostip hostip.c

hostip_asm: hostip_asm.o
	gcc -m32 -o hostip_asm hostip_asm.o
	rm -f hostip_asm.o

hostip_asm.o: hostip.asm
	nasm -f elf -g hostip.asm -o hostip_asm.o

clean:
	rm -f hostip
	rm -f hostip_asm
