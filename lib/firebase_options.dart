import 'package:firebase_core/firebase_core.dart';

class FirebaseOptionsFor {
  static const FirebaseOptions staff = FirebaseOptions(
    apiKey: 'AIzaSyDLTzJ-9OIwUiSQ1Yk7TSAbfnwZXaKoYFs',
    appId: '1:77722937663:android:b835f8b5368678496f0b8a',
    messagingSenderId: '77722937663',
    projectId: 'gym-management-system-b3e71',
    storageBucket: 'gym-management-system-b3e71.firebasestorage.app',
  );

  static const FirebaseOptions client = FirebaseOptions(
    apiKey: 'AIzaSyDLTzJ-9OIwUiSQ1Yk7TSAbfnwZXaKoYFs',
    appId: '1:77722937663:android:b10da332871e9a916f0b8a',
    messagingSenderId: '77722937663',
    projectId: 'gym-management-system-b3e71',
    storageBucket: 'gym-management-system-b3e71.firebasestorage.app',
  );

  static const FirebaseOptions superAdmin = FirebaseOptions(
    apiKey: 'AIzaSyDLTzJ-9OIwUiSQ1Yk7TSAbfnwZXaKoYFs',
    appId: '1:77722937663:android:ad6918c302ab83a16f0b8a',
    messagingSenderId: '77722937663',
    projectId: 'gym-management-system-b3e71',
    storageBucket: 'gym-management-system-b3e71.firebasestorage.app',
  );

  // Web app registered in the Firebase console. Its apiKey and appId are
  // web-specific (different from the Android apps above); everything else is
  // the same project. These values are also mirrored — by hand, since a
  // service worker can't read Dart — in web/firebase-messaging-sw.js, so keep
  // the two in sync.
  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyDceGMu8twuV5li69vF6agjvOv1hfQfCJE',
    appId: '1:77722937663:web:3885a408e0863f556f0b8a',
    messagingSenderId: '77722937663',
    projectId: 'gym-management-system-b3e71',
    authDomain: 'gym-management-system-b3e71.firebaseapp.com',
    storageBucket: 'gym-management-system-b3e71.firebasestorage.app',
  );
}