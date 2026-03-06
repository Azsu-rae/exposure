import de.huxhorn.sulky.ulid.ULID

case class Store(
  id: ULID,
  name: String,
  description: String,
  ownerId: ULID
)
