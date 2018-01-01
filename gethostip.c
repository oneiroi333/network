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
	int status;

	if (argc < 2) {
		fprintf(stderr, "Usage: %s hostname\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	memset(&hints, 0, sizeof(struct addrinfo));

	/* Lookup IPv4 */
	hints.ai_family = AF_INET;
	status = getaddrinfo(argv[1], NULL, &hints, &result);
	if (status != 0) {
		fprintf(stderr, "[Error IPv4]: %s\n", gai_strerror(status));
	} else {
		print_result(result);
	}

	/* Lookup IPv6 */
	hints.ai_family = AF_INET6;
	status = getaddrinfo(argv[1], NULL, &hints, &result);
	if (status != 0) {
		fprintf(stderr, "[Error IPv6]: %s\n", gai_strerror(status));
	} else {
		print_result(result);
	}

	freeaddrinfo(result);

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
		switch(rp->ai_family) {
			case AF_INET:
				++first;
				addr = &(((struct sockaddr_in *) rp->ai_addr)->sin_addr);
				inet_ntop(AF_INET, addr, ipv4_addr, INET_ADDRSTRLEN); /* network to ascii */
				if (first == 1) {
					fprintf(stdout, "===============[ IPv4 ]===============\n");
					fprintf(stdout, "Address: %s\n", ipv4_addr);
				}
				break;
			case AF_INET6:
				++first6;
				addr6 = &(((struct sockaddr_in6 *) rp->ai_addr)->sin6_addr);
				inet_ntop(AF_INET6, addr6, ipv6_addr, INET6_ADDRSTRLEN); /* network to ascii */
				if (first6 == 1) {
					fprintf(stdout, "===============[ IPv6 ]===============\n");
					fprintf(stdout, "Address: %s\n", ipv6_addr);
				}
				break;
			default:
				;
		}
		if (first == 1 || first6 == 1) {
			fprintf(stdout, "Socket type: ");
		} else {
			fprintf(stdout, ", ");
		}
		switch(rp->ai_socktype) {
			case SOCK_STREAM:
				fprintf(stdout, "TCP");
				break;
			case SOCK_DGRAM:
				fprintf(stdout, "UDP");
				break;
			case SOCK_RAW:
				fprintf(stdout, "RAW");
				break;
			default:
				fprintf(stdout, "OTHER");
		}
	}
	fprintf(stdout, "\n");
}
