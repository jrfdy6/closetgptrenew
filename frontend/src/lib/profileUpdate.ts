type ProfileEditorValues = {
  name?: string;
  gender?: string;
  stylePreferences?: readonly string[] | null;
};

/** Send only fields edited by the profile screen, never its full server readback. */
export function buildProfileUpdate(profile: ProfileEditorValues) {
  return {
    ...(profile.name !== undefined ? { name: profile.name } : {}),
    ...(profile.gender !== undefined ? { gender: profile.gender } : {}),
    ...(Array.isArray(profile.stylePreferences) ? { stylePreferences: [...profile.stylePreferences] } : {}),
  };
}
