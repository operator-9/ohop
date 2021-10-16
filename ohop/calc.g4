grammar calc;

statements: (statement NL)* ;
statement: assign | expr ;
assign: ID '=' expr ;
expr: atom (op expr)? ;
atom: ID | NUM ;
op: '+' | '-' ;
NL: [\r\n]+ ;
ID: [A-Za-z]+ ;
NUM: [0-9]+ ;
WS: [ \t]+ -> skip ;
