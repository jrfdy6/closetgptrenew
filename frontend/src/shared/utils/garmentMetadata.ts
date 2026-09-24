import { VisualAttributesSchema, type ClothingItem } from '../types';

/** Legacy metadata is persisted unchanged; scoring only consumes validated attributes. */
export function readVisualAttributes(item: Pick<ClothingItem, 'metadata'>) {
  const result = VisualAttributesSchema.safeParse(item.metadata?.visualAttributes);
  return result.success ? result.data : undefined;
}
