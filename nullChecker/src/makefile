CC = g++
DEBUG = -O3
CFLAGS = -fPIC -std=c++11 $(DEBUG) -c
LFLAGS = -shared -std=c++11 $(DEBUG)

RM = rm -f  			# rm command
TARGET_LIB = FAHES.so 	# Shared object target
SRCS = $(shell ls *.cpp)
OBJS = $(SRCS:.cpp=.o)

all: $(TARGET_LIB)

$(TARGET_LIB): $(OBJS)
	$(CC) $(LFLAGS) -o $(TARGET_LIB) $(OBJS)

clean:
	-$(RM) $(TARGET_LIB) $(OBJS)
rmo:
	-$(RM) $(OBJS)