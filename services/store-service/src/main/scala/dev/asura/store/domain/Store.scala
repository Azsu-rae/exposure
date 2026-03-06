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
      id: String,
      name: String,
      description: String,
      ownerId: String
  ): Store = {

    require(name.nonEmpty, "Store name cannot be empty")

    Store(id, name, description, ownerId)
  }
}
