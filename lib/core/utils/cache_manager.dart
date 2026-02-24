class CacheManager {
  static final CacheManager _instance = CacheManager._internal();
  factory CacheManager() => _instance;
  CacheManager._internal();
  
  final Map<String, CacheEntry> _cache = {};
  
  // Store data in cache
  void store(String key, dynamic data, {Duration? duration}) {
    final expiry = DateTime.now().add(duration ?? const Duration(minutes: 30));
    _cache[key] = CacheEntry(data: data, expiry: expiry);
  }
  
  // Get data from cache
  T? get<T>(String key) {
    final entry = _cache[key];
    if (entry == null) return null;
    
    // Check if expired
    if (DateTime.now().isAfter(entry.expiry)) {
      _cache.remove(key);
      return null;
    }
    
    return entry.data as T?;
  }
  
  // Clear specific key
  void clear(String key) {
    _cache.remove(key);
  }
  
  // Clear all cache
  void clearAll() {
    _cache.clear();
  }
  
  // Check if key exists and is valid
  bool has(String key) {
    final entry = _cache[key];
    if (entry == null) return false;
    
    if (DateTime.now().isAfter(entry.expiry)) {
      _cache.remove(key);
      return false;
    }
    
    return true;
  }
}

class CacheEntry {
  final dynamic data;
  final DateTime expiry;
  
  CacheEntry({required this.data, required this.expiry});
}

// Cache Keys
class CacheKeys {
  static const String branches = 'branches';
  static const String services = 'services';
  static const String userProfile = 'user_profile';
  
  static String branchDetails(int branchId) => 'branch_$branchId';
  static String serviceDetails(int serviceId) => 'service_$serviceId';
}
