### BananaPlus

## Introduction
BananaPlus is a custom programming language that i made with Python. BananaPlus scripts have the file extension '.bp'.

## Documentation and getting started:
[The docs and tutorial](https://spazelectro.github.io/ZSharpDocs/#/README)

## Installation
Downloading or installing is very simple, ONLY FOR WINDOWS:
### Windows
1. Navigate to [the most recent release](https://github.com/pronoob742/BananaPlus/releases) and download `BananaPlus_setup.exe`.
2. Open the file `BananaPlus_setup.exe` and follow the steps.
3. Inside is a single file titled `ZSharp-Setup.exe`. Run it, and follow the setup instructions.

## Library
You can add any .bp files in location "C:\BananaPlus\libs".<br>
To import libs:
```js
// you dont need to add .bp in the end of the name
import "lib_name" as lib
```

## this is the main things in the language
```js
// Comments are indicated by two forward slashes
// They can only be on their own line

// you can import files from your current workspace
import "file_name.bp" as lib

// you can define variables
// you can use them any place in the file
let a = "Hello"

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
