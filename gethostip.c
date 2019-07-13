#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void print_result(struct addrinfo *result);

int
main(int argc, char *argv[])
{
	struct addrinfo hints;
	struct addrinfo *result;
	int err;

	if (argc < 2) {
		fprintf(stderr, "Usage: %s <hostname>\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	/* Lookup IP */
	memset(&hints, 0, sizeof(struct addrinfo));
	hints.ai_family = AF_UNSPEC; /* IPv4 and IPv6 */
	err = getaddrinfo(argv[1], NULL, &hints, &result);
	if (err) {
		fprintf(stderr, "[Error] %s\n", gai_strerror(err));
		exit(EXIT_FAILURE);
	} else {
		print_result(result);
		freeaddrinfo(result);
	}
	exit(EXIT_SUCCESS);
}

void
print_result(struct addrinfo *result)
{
	struct addrinfo *rp;
	struct in_addr *addr;
	struct in6_addr *addr6;
	char ipv4_addr[INET_ADDRSTRLEN];
	char ipv6_addr[INET6_ADDRSTRLEN];
	static int first = 0;
	static int first6 = 0;

	for (rp = result; rp != NULL; rp = rp->ai_next) {
		/* IPv4 and IPv6 got printed, we can stop now */
		if (first > 0 && first6 > 0) {
			break;
		}
		switch(rp->ai_family) {
			case AF_INET:
				++first;
				if (first != 1) {
					continue;
				}
				addr = &(((struct sockaddr_in *) rp->ai_addr)->sin_addr);
				/* Get string representation of IP addr */
				inet_ntop(AF_INET, addr, ipv4_addr, INET_ADDRSTRLEN);
				fprintf(stdout, "IPv4: %s\n", ipv4_addr);
				break;
			case AF_INET6:
				++first6;
				if (first6 != 1) {
					continue;
				}
				addr6 = &(((struct sockaddr_in6 *) rp->ai_addr)->sin6_addr);
				/* Get string representation of IP addr */
				inet_ntop(AF_INET6, addr6, ipv6_addr, INET6_ADDRSTRLEN);
				fprintf(stdout, "IPv6: %s\n", ipv6_addr);
				break;
			default:
				;
		}
	}
}
