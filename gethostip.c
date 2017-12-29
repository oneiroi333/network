#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define NOT_INIT '.'

int
main(int argc, char *argv[])
{
	struct addrinfo hints;
	struct addrinfo *result, *rp;
	int status;
	char ipv4_addr[INET_ADDRSTRLEN] = {NOT_INIT};
	char ipv6_addr[INET6_ADDRSTRLEN] = {NOT_INIT};

	if (argc < 2) {
		fprintf(stderr, "Usage: %s hostname\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	memset(&hints, 0, sizeof(struct addrinfo));
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = 0;
	hints.ai_flags = 0;
	hints.ai_protocol = 0;

	status = getaddrinfo(argv[1], NULL, &hints, &result);
	if (status != 0) {
		fprintf(stdout, "Sry, could not lookup: %s\n", argv[1]);
		exit(EXIT_FAILURE);
	}

	for (rp = result; rp != NULL; rp = rp->ai_next) {
		/* IPv4 */
		if (rp->ai_family == AF_INET) {
			if (ipv4_addr[0] == NOT_INIT) {
				inet_ntop(AF_INET, &(((struct sockaddr_in *) rp->ai_addr)->sin_addr), ipv4_addr, INET_ADDRSTRLEN);
			}
		}
		/* IPv6 */
		if (rp->ai_family == AF_INET6) {
			if (ipv6_addr[0] == NOT_INIT) {
				inet_ntop(AF_INET6, &(((struct sockaddr_in6 *) rp->ai_addr)->sin6_addr), ipv6_addr, INET6_ADDRSTRLEN);
			}
		}
		/* Found both ipv4 and ipv6 addresses */
		if (ipv4_addr[0] != NOT_INIT && ipv6_addr[0] != NOT_INIT) {
			break;
		}
	}

	if (ipv4_addr[0] != NOT_INIT) {
		fprintf(stdout, "IPv4: %s\n", ipv4_addr);
	}
	if (ipv6_addr[0] != NOT_INIT) {
		fprintf(stdout, "IPv6: %s\n", ipv6_addr);
	}

	freeaddrinfo(result);

	exit(EXIT_SUCCESS);
}
