import ply.lex as lex

reserved = {
  'Maj' : 'MAJ',
  'bsig0': 'BSIG0',
  'in' : 'INPUT',
  'bit32': 'BIT32',
  'out': 'OUTPUT',
  'var': 'ASSIGN',
  'loop': 'LOOP',
  'const': 'CONSTANT',
  'Ch': 'CH',
  'bit': 'BIT',
  'bit256': 'BIT256',
  'bit512': 'BIT512',
  'bit1024': 'BIT1024',
  'bit2048': 'BIT2048',
  'bit4': 'BIT4',
  'Add':'ADD',
  'bsig1':'BSIG1',
  'lsig0':'LSIG0',
  'lsig1':'LSIG1',
  'move': 'MOVE',
  'shab1': 'FIRSTBLOCK',
}

tokens = ['LBRACK', 'RBRACK', 'COLON', 'ID', 'EQUALS', 'LPAREN', 'RPAREN', 'INPUT', 'COMMA', 'OUTPUT', 'ASSIGN', 'LOOP', 'LBRACE', 'RBRACE', 'NUMBER', 'CONSTANT', 'MAJ', 'CH', 'BIT', 'BIT4', 'BIT32', 'BIT256', 'BIT512', 'BIT1024', 'BIT2048', 'BSIG0', 'BSIG1', 'LSIG0', 'LSIG1', 'ADD', 'MOVE', 'FIRSTBLOCK', 'STAR']
t_ignore = ' \t'
t_EQUALS = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_COLON = r':'
t_COMMA = r','
t_STAR = r'\*'

def t_ID(t):
  r'[a-zA-Z_][a-zA-Z_0-9]*'
  t.type = reserved.get(t.value,'ID')    # Check for reserved words
  return t

def t_NUMBER(t):
 r'\d+'
 t.value = int(t.value)
 return t

def t_error(t):
  print("Illegal character '%s'" % t.value[0])
  t.lexer.skip(1)

def t_newline(t):
  r'\n+'
  t.lexer.lineno += len(t.value)

lexer = lex.lex() # Build the lexer

# Test it out

# Give the lexer some input
def getTokens(f, s=None):
  if s==None:
    with open(f, "r") as f:
      lexer.input(f.read())
  else:
    lexer.input(s)
  # Tokenize
  toks = []
  while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    toks.append((tok.type,tok.value,tok.lineno))
  return toks

