# What is a UUID

A **UUID** stands for **Universally Unique Identifier**. It is a **128-bit identifier designed to be unique across space and time**, even if it is generated on different machines without coordination.

In practice, it's used as a **globally unique ID** for things like:

- database records
- users
- stores
- orders
- files
- distributed systems

## What a UUID looks like

A UUID is usually represented as a **36-character string**:

```
550e8400-e29b-41d4-a716-446655440000
```

Structure:

```
8 chars - 4 chars - 4 chars - 4 chars - 12 chars
```

Example parts:

```
550e8400
e29b
41d4
a716
446655440000
```

These characters are **hexadecimal** (0-9 and a-f).

---

## Why UUIDs are used

The main advantage is **uniqueness without a central authority**.

Example problem with auto-increment IDs:

```
Store 1
Store 2
Store 3
```

This works for **one database**, but breaks in distributed systems:

```
Service A creates Store 1
Service B also creates Store 1
```

Now you have a conflict.

UUID solves this:

```
Store A -> 7c8e1b10-8e8c-4c61-8bfa-2b9f9f0d5c2c
Store B -> a1f92b33-22f7-4c61-9caa-7d4e8b9caa01
```

They will **almost certainly never collide**.

---

## Why UUIDs are good for microservices

In a **microservice architecture**, services often generate IDs independently.

Example:

```
user-service
store-service
order-service
```

If each service generates UUIDs:

- they don't need a **central ID generator**
- they don't need a **shared database**
- services can operate independently

This is why UUIDs are very common in distributed systems.

---

## One more advantage: security

With incremental IDs:

```
/stores/1
/stores/2
/stores/3
```

A user can **enumerate all stores**.

With UUID:

```
/stores/3c9f2a8f-84cb-4c76-9f3a-2f4db0a5c0ef
```

It's **practically impossible to guess another ID**.

---

# How UUIDs work

The key idea is that **UUIDs aren't guaranteed unique by checking a database** — they are **so astronomically unlikely to collide that we treat them as unique**.

---

## UUID size

A UUID is **128 bits**.

That means there are:

```
2^128 possible UUIDs
```

Which equals roughly:

```
340,282,366,920,938,463,463,374,607,431,768,211,456
```

That's **340 undecillion** possible values.

For comparison:

- grains of sand on Earth ≈ **7.5 × 10¹⁸**
- UUID possibilities ≈ **3.4 × 10³⁸**

So the space is **absurdly huge**.

---

## UUID v4 (the common one)

When you call:

```scala
UUID.randomUUID()
```

Java generates a **UUID version 4**, which is based on **cryptographically strong random numbers**.

Example:

```
7c8e1b10-8e8c-4c61-8bfa-2b9f9f0d5c2c
```

Most bits are random.

---

## Collision probability

Even if you generated **billions of UUIDs**, the chance of a collision is still negligible.

A famous estimate:

If you generate **1 billion UUIDs per second for 100 years**, the chance of a collision is still extremely tiny.

Mathematically, collisions follow the **birthday paradox**, but because the number space is so huge, the risk is effectively zero.

## Different types of UUIDs

UUIDs aren't always random. There are several versions.

### UUID v1

Uses:

- timestamp
- machine MAC address

So it looks like:

```
time + machine id
```

Guarantees uniqueness but leaks machine info.

---

### UUID v4 (most common)

Uses **random numbers**.

```
random 122 bits
```

This is what Java uses.

---

### UUID v7 (newer)

Uses:

```
timestamp + randomness
```

Benefits:

- sortable by time
- still globally unique

Modern databases increasingly prefer this.

---

## Why databases sometimes dislike UUID

Random UUIDs have a drawback:

Database indexes prefer **ordered values**.

Example:

```
1
2
3
4
```

Indexes grow nicely.

But UUIDs look random:

```
7c8e1b10...
2f4db0a5...
a1f92b33...
```

So inserts scatter across the index tree.

This can slow large databases.

That's why modern systems sometimes use **UUIDv7 or ULID** instead.

---

# ULIDs

A **ULID** stands for **Universally Unique Lexicographically Sortable Identifier**.

It is also **128 bits**, just like a UUID, but structured differently.

Structure:

```
timestamp (48 bits) + randomness (80 bits)
```

So it contains:

- **time component** → when it was created
- **random component** → to avoid collisions

Example ULID:

```
01HV7Y4J6N6E6K1G0X4Q8A9Z2P
```

It uses **Base32 encoding**, so it's shorter and URL-friendly.

---

## Why ULID is nice for databases

ULIDs are **sortable by creation time**.

Example:

```
01HV7Y4J6N6E6K1G0X4Q8A9Z2P
01HV7Y4J9M8H3X6Y2T9J7F4R1K
01HV7Y4JDF8P1B0M5Z9S6C3Q2T
```

Later records have **larger IDs**.

This is extremely useful because databases like **ordered inserts**.

Compare that to UUIDv4:

```
7c8e1b10-8e8c-4c61...
2f4db0a5-3d12-49a0...
a1f92b33-22f7-4c61...
```

Totally random → worse index performance.

---

## ULID advantages

| Feature | UUIDv4 | ULID |
|---------|--------|------|
| Globally unique | ✅ | ✅ |
| Random | ✅ | partly |
| Sortable | ❌ | ✅ |
| URL friendly | ❌ | ✅ |
| Shorter | ❌ | ✅ |
| Database friendly | ❌ | ✅ |

ULIDs solve the **database index fragmentation problem**.

---

## ULID readability

ULIDs are easier for humans.

Example:

```
UUID:
7c8e1b10-8e8c-4c61-8bfa-2b9f9f0d5c2c
```

vs

```
ULID:
01HV7Y4J6N6E6K1G0X4Q8A9Z2P
```

Shorter and cleaner.

---

## ULID collision probability

ULID still has **80 random bits**.

That gives:

```
2^80 possibilities per millisecond
```

Which is about:

```
1.2 trillion trillion
```

So collisions are still **practically impossible**.

---

## Big systems that use ULID-style IDs

Many modern systems moved away from UUIDv4:

Examples:

- **Cloudflare**
- **Supabase**
- **Stripe-like systems**
- many Go / Rust backend stacks

Also related formats:

- **ULID**
- **KSUID**
- **Snowflake IDs**
- **UUIDv7** (new standard similar to ULID)

---

## Using ULID in Scala

We can use a library like:

```
de.huxhorn.sulky:de.huxhorn.sulky.ulid
```

Example:

```scala
import de.huxhorn.sulky.ulid.ULID

val ulid = new ULID()
val id = ulid.nextULID() // this is a String!

println(id)
```

Example output:

```
01HV7Y4J6N6E6K1G0X4Q8A9Z2P
```
