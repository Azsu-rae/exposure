package store.domain

import de.huxhorn.sulky.ulid.ULID

case class Store(
    id: String,
    name: String,
    description: String,
    ownerId: String
)

object Store {

  def create(
      name: String,
      description: String
  ): Store = {

    require(name.nonEmpty, "Store name cannot be empty")

    val ulid = new ULID()
    Store(ulid.nextULID(), name, description, ulid.nextULID())
  }
}
