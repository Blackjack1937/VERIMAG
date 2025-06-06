SRC      := magic_crash.c          
BIN      := ../bin/magic_crash
BIN_COV  := ../bin/magic_crash_cov
CFLAGS   := -O2 -static
CC_AFL   ?= afl-clang-fast       

all: $(BIN)

$(BIN): $(SRC)
	$(CC) $(CFLAGS) -o $@ $<

cov: $(BIN_COV)

$(BIN_COV): $(SRC)
	$(CC_AFL) -O2 -static \
	          -fsanitize-coverage=trace-pc-guard \
	          -fno-sanitize-recover \
	          -o $@ $<

clean:
	$(RM) $(BIN)

BIN_COV := ../bin/magic_crash_cov
CC_AFL  ?= afl-clang-fast                 #afl
