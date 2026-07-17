import 'package:flutter/material.dart';
import '../../../core/api/api_service.dart';
import '../../../shared/models/owner_model.dart';
import '../../../shared/models/gym_model.dart';

class SuperAdminProvider extends ChangeNotifier {
  final ApiService _apiService;

  bool _isLoading = false;
  String? _error;
  List<OwnerModel> _owners = [];
  List<GymModel> _gyms = [];
  List<dynamic> _allStaff = [];
  Map<String, dynamic>? _stats;

  SuperAdminProvider(this._apiService);

  ApiService get apiService => _apiService;
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<OwnerModel> get owners => _owners;
  List<GymModel> get gyms => _gyms;
  List<dynamic> get allStaff => _allStaff;
  Map<String, dynamic>? get stats => _stats;

  int get totalOwners => _owners.length;
  int get activeOwners => _owners.where((o) => o.isActive).length;
  int get totalGyms => _gyms.length;
  int get activeGyms => _gyms.where((g) => g.isActive).length;
  int get totalBranches => _gyms.fold(0, (sum, g) => sum + g.branchCount);
  int get totalCustomers => _gyms.fold(0, (sum, g) => sum + g.customerCount);
  int get totalStaff => _gyms.fold(0, (sum, g) => sum + g.staffCount);

  Future<void> loadDashboardData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await Future.wait([
        _loadOwners(),
        _loadGyms(),
        _loadAllStaff(),
      ]);

      _stats = {
        'total_owners': _owners.length,
        'active_owners': _owners.where((o) => o.isActive).length,
      };

      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> _loadOwners() async {
    final response = await _apiService.get('/api/users?role=owner&per_page=100');
    final data = response.data;
    if (data['success'] == true) {
      final items = (data['data']['items'] as List?) ?? [];
      _owners = items
          .map((o) => OwnerModel.fromJson(o as Map<String, dynamic>))
          .toList();
    }
  }

  Future<void> _loadGyms() async {
    try {
      final response = await _apiService.get('/api/gyms');
      final data = response.data;
      if (data['success'] == true) {
        final items = (data['data'] as List?) ?? [];
        _gyms = items
            .map((g) => GymModel.fromJson(g as Map<String, dynamic>))
            .toList();
      }
    } catch (e) {
      debugPrint('⚠️ Gyms load failed: $e');
      _gyms = [];
    }
  }

  Future<void> _loadAllStaff() async {
    try {
      final response = await _apiService.get('/api/users?per_page=100');
      final data = response.data;
      if (data['success'] == true) {
        _allStaff = (data['data']['items'] as List?) ?? [];
      }
    } catch (e) {
      debugPrint('⚠️ Staff load failed: $e');
      _allStaff = [];
    }
  }

  /// Branches of one gym, with per-branch stats (drill-down).
  Future<List<dynamic>> fetchGymBranches(int gymId) async {
    final response = await _apiService.get('/api/gyms/$gymId/branches');
    final data = response.data;
    if (data['success'] == true) {
      return (data['data'] as List?) ?? [];
    }
    return [];
  }

  /// Activate/deactivate any gym.
  Future<Map<String, dynamic>> toggleGymStatus(GymModel gym) async {
    try {
      final newStatus = !gym.isActive;
      await _apiService.put('/api/gyms/${gym.id}', data: {'is_active': newStatus});
      final index = _gyms.indexWhere((g) => g.id == gym.id);
      if (index != -1) {
        _gyms[index] = gym.copyWith(isActive: newStatus);
        notifyListeners();
      }
      return {'success': true, 'active': newStatus};
    } catch (e) {
      return {'success': false, 'message': e.toString()};
    }
  }

  /// Edit any gym's core settings.
  Future<Map<String, dynamic>> updateGym(int gymId, Map<String, dynamic> fields) async {
    try {
      final response = await _apiService.put('/api/gyms/$gymId', data: fields);
      final data = response.data;
      if (data['success'] == true) {
        final updated = GymModel.fromJson(data['data'] as Map<String, dynamic>);
        final index = _gyms.indexWhere((g) => g.id == gymId);
        if (index != -1) {
          // Keep the counts the list endpoint computed — the update
          // response doesn't include them.
          _gyms[index] = updated.copyWith(
            branchCount: _gyms[index].branchCount,
            customerCount: _gyms[index].customerCount,
            staffCount: _gyms[index].staffCount,
          );
          notifyListeners();
        }
        return {'success': true};
      }
      return {'success': false, 'message': data['error'] ?? 'Update failed'};
    } catch (e) {
      return {'success': false, 'message': e.toString()};
    }
  }

  /// Creates a new gym owner account.
  /// The owner will log in and complete the gym setup wizard themselves.
  Future<Map<String, dynamic>> createOwner({
    required String fullName,
    required String username,
    required String password,
    String? email,
    String? phone,
  }) async {
    try {
      final response = await _apiService.post('/api/users', data: {
        'username': username,
        'full_name': fullName,
        'password': password,
        'email': email ?? '$username@owner.com',
        'role': 'owner',
        if (phone != null && phone.isNotEmpty) 'phone': phone,
      });

      final data = response.data;

      if (data['success'] == true) {
        final newOwner = OwnerModel.fromJson(data['data'] as Map<String, dynamic>);
        _owners.insert(0, newOwner);
        notifyListeners();

        return {
          'success': true,
          'message': 'Owner "$fullName" created successfully. They can now log in and set up their gym.',
          'owner': newOwner.toJson(),
        };
      } else {
        return {
          'success': false,
          'message': data['error'] ?? 'Failed to create owner',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Failed to create owner: $e',
      };
    }
  }

  Future<Map<String, dynamic>> toggleOwnerStatus(int ownerId) async {
    try {
      final index = _owners.indexWhere((o) => o.id == ownerId);
      if (index == -1) return {'success': false, 'message': 'Owner not found'};

      final owner = _owners[index];
      final newStatus = !owner.isActive;

      await _apiService.put('/api/users/$ownerId', data: {'is_active': newStatus});

      _owners[index] = OwnerModel(
        id: owner.id,
        username: owner.username,
        fullName: owner.fullName,
        email: owner.email,
        phone: owner.phone,
        isActive: newStatus,
        createdAt: owner.createdAt,
        lastLogin: owner.lastLogin,
      );
      notifyListeners();

      return {
        'success': true,
        'message': newStatus ? 'Owner activated' : 'Owner deactivated',
      };
    } catch (e) {
      return {'success': false, 'message': e.toString()};
    }
  }

  Future<void> refresh() async {
    await loadDashboardData();
  }
}
