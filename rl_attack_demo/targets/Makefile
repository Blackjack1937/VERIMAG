BIN   := ../bin/magic_crash
CFLAGS:= -O2 -static

all: $(BIN)

$(BIN): magic_crash.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	$(RM) $(BIN)
