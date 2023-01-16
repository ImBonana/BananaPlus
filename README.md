# BananaPlus

## Introduction
BananaPlus is a custom programming language that i made with Python. BananaPlus scripts have the file extension '.bp'.

## Installation
Downloading or installing is very simple, ONLY FOR WINDOWS:
### Windows
1. Navigate to [the most recent release](https://github.com/pronoob742/BananaPlus/releases) and download `BananaPlus_setup.exe`.
2. Open the file `BananaPlus_setup.exe` and follow the steps.
3. Inside is a single file titled `BananaPlus_setup.exe`. Run it, and follow the setup instructions.

## Vs Code
If you use vs code you can download [BananaPlus Vs Extension](https://marketplace.visualstudio.com/items?itemName=ImBanana.bananaplus)

##  How to run
Open command line and type `BananaPlus <path>`.<br>
To open the `BananaPlus` console:
1. Open command line.
2. Run the command `BananaPlus-Console`.

## Library
You can add any .bp files in location "C:\BananaPlus\libs".<br>
To import libs:
```js
// You dont need to add .bp in the end of the name
// You can change the 'lib' to whatever you want
import "lib_name" as lib

// To access the variable from other file you need to add the 'public' keyword
public let a = "You can see me"

// You can add 'private' keyword before
// By default, all variables are private
private let b = "You can't see me"

// you can to the same to function
```

## this is the main things in the language
```js
// Comments are indicated by two forward slashes
// They can only be on their own line

// you can import files from your current workspace
import "file_name.bp" as lib

// you can define variables
// you can use them any place in the file
let a = 1

// you can use
a -= 1
a += 1
// instead of
a = a - 1
a = a + 1

// Use if statement to check values
if a == "Hello" then
    print("Is hello")
else
    print("idk")
end

// you can have a switch statment
switch "a" then
    case "b" then
        print("its b")
    end
  
    case "a" then
        print("its a")
    end
  
    default
        print("idk")
    end
end

// You can have for loop you can change the 'i' ro anything you want
// the step key word is optinal
for i = 0 to 10 step 2 then
    print(i)
end

// you can have while loop
// you can change this to any condition
//     v
while true then
    break
end

// prints staff
print("Hello, World!")

// Declare new function with 'func', then it's name, and the names of any input variables.
// You can make optinal variables when you add ? after the variable name
// You can return from the function (Optinal)
func test(a, b?)
{
    print("This is from the function!")
    
    return true
}
```
