#!/usr/bin/env octave 

%This is an octave example.

function board()
    
    printf('A0D B0D C0D D0D E0D\n');

end


function guess()
    
    let = 65 + floor(rand*10);
    ind = floor(rand*10);
    
    printf('%c%d\n', let, ind);
end


function mainloop()

    running = 1;
    while running
        inp = input(">","s");
        
        if (inp(1)=='K')
            running = 0;
        elseif (inp(1)=='F')
            guess();
        elseif (inp(1)=='N')
            board();
        else 
            printf('\n');
        end
        
    end
    
end
    
mainloop();
