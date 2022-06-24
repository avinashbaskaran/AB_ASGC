#include <Python.h>

#include <iostream>
int main(){

Py_Initialize();
PyRun_SimpleString("print('it Worked')");
Py_Finalize();

return 0;
}



