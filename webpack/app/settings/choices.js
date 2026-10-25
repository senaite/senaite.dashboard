// Choices of a filter, asked for once per page

const cache = new Map();

export function loadChoices(api, dataset, field) {
  const key = `${dataset}/${field}`;
  if (!cache.has(key)) {
    cache.set(key, api.choices(dataset, field)
      .then((answer) => answer.choices)
      .catch((error) => {
        cache.delete(key);
        throw error;
      }));
  }
  return cache.get(key);
}
