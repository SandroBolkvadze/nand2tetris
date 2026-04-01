// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

// PSEUDOCODE:

// function LISTEN():
//     while True:
//         if MEM[@KBD] == 0:
//             color = 0
//         else:
//             color = -1
// 
//         call FILL(color)
// 
//
// function FILL(color):
//     address = @SCREEN
//     count = 8192
// 
//     while count > 0:
//         DECREMENT count
// 
//         MEM[address] = color
//          
//         INCREMENT address
//
//     return


// Infinite loop listening for keyboard input.
(LISTEN)
    @KBD
    D=M

    @color
    M=0

    @LOOP_CONTINUE
    D; JEQ

    @color
    M=-1

(LOOP_CONTINUE)
    @FILL
    0; JMP

(LISTEN_END)
    @LISTEN_END
    0; JMP


// Color screen with @color.
(FILL)
    @SCREEN
    D=A

    @address
    M=D

    @8192
    D=A
    
    @count
    M=D

(FILL_LOOP)
    @count
    D=M

    @FILL_RETURN
    D; JLE

    @count
    M=M-1

    @color
    D=M

    @address
    A=M
    
    M=D

    @address
    M=M+1

    @FILL_LOOP
    0; JMP

(FILL_RETURN)
    @LISTEN
    0; JMP
