"""Read the complete active wardrobe across supported owner-field versions."""
OWNER_FIELDS = ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId')
DELETED_FIELDS = ('deleted', 'isDeleted', 'deletedAt', 'deleted_at')


def wardrobe_owned_by(item, user_id):
    if not isinstance(item, dict) or not isinstance(user_id, str) or not user_id:
        return False
    owners = [item[key] for key in OWNER_FIELDS if item.get(key) is not None]
    return bool(owners) and all(isinstance(owner, str) and owner == user_id for owner in owners)


def canonical_owned_garment(item, user_id, identifier):
    """Normalize an already verified snapshot for consumers; never write aliases."""
    if not wardrobe_owned_by(item, user_id):
        raise ValueError('Garment ownership could not be verified')
    return {**item, 'id': identifier, 'userId': user_id}


def owned_wardrobe_documents(db, user_id, transaction=None):
    """Union scoped queries, rejecting conflicting ownership and deleted rows.

    A failure on any query propagates; a partial wardrobe is not a confirmed
    empty/smaller wardrobe. No collection-wide fallback is permitted.
    """
    from google.cloud.firestore_v1.base_query import FieldFilter
    if not isinstance(user_id, str) or not user_id:
        raise ValueError('A verified account is required')
    options = {'transaction': transaction} if transaction is not None else {}
    documents = {}
    for field in OWNER_FIELDS:
        for snapshot in db.collection('wardrobe').where(filter=FieldFilter(field, '==', user_id)).stream(**options):
            if snapshot.id in documents:
                continue
            item = snapshot.to_dict() or {}
            if wardrobe_owned_by(item, user_id) and not any(item.get(key) for key in DELETED_FIELDS):
                documents[snapshot.id] = snapshot
    return list(documents.values())
