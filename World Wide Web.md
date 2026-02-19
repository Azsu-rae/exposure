
At the birth of the **internet**, two common architecture patterns were used by applications:

**C/S (Client/Server)**: as clients as software services. e.g.
- Email clients talking to email servers
- Database clients talking to DB servers
**B/S (Browser/Server)**: one client for all software services. All you would need is a browser + URL. This was revolutionary because the browser became the universal client

# Uniform Resource Identifier (URI)

URI is a **standard way to write an identifier for a resource**. It can be one of:

- **Uniform Resource Locator (URL)**

Format:

```<scheme>://<user>:<password>@<host>:<port>/<path>;<params>?<query>#<fragment> ```

**scheme**: protocol used (e.g. HTTP, FTP)
**user & password**: authentication information
**host**: IP address or domain name
**port**: port used by the service to connect to
**path**: to the resource in the host

- **Uniform Resource Name (URN)**

URN is the name of an internet resource. Used in P2P