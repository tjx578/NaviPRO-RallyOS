/** Only explicit allowlisted origins can supply remote terrain/imagery/3D datasets.
 * Asset permissions/credits must be verified separately. Never embed credentials. */
export function allowlistedAssetUrl(raw:string, extraOrigins:string[]=[]):string {
  const url=new URL(raw,window.location.origin);
  if(!['http:','https:'].includes(url.protocol)) throw new Error('Unsupported asset URL scheme');
  if(url.username||url.password) throw new Error('URL credentials prohibited');
  const allowed=new Set([window.location.origin,...extraOrigins]);
  if(!allowed.has(url.origin)) throw new Error('Asset provider is not explicitly allowlisted');
  if(url.pathname.includes('\\') || /%2f|%5c/i.test(raw)) throw new Error('Ambiguous encoded asset path');
  return url.href;
}
