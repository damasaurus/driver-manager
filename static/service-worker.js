self.addEventListener("push", function (event) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: "/static/icon-192.png", // make sure this file exists
      badge: "/static/icon-192.png"
    };
  
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  });
  