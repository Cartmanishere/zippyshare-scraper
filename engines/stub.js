const document = {
  getElementById(key) {
    if (!this[key]) {
      this[key] = {}
    }
    return this[key];
  }
}