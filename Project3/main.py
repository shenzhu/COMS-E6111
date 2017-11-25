import sys

# Global Variables
FILE_NAME = ""
MIN_SUP = 0.0
MIN_CONF = 0.0


def read_parameters():
    inputs = sys.argv

    global FILE_NAME, MIN_SUP, MIN_CONF
    FILE_NAME = inputs[1]
    MIN_SUP = float(inputs[2])
    MIN_CONF = float(inputs[3])

    # Print to console
    print "min_sup: " + str(MIN_SUP)
    print "min_conf: " + str(MIN_CONF)


def main():
 	read_parameters()


if __name__ == '__main__':
	main()