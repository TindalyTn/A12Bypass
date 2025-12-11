?php
// --- Database Configuration ---
$servername = "localhost";
$username = "";
$password = "";
$dbname = "";

// --- Main Logic ---

// 1. Check if the 'sn' parameter exists and is not empty
if (!isset($_GET['sn']) || empty(trim($_GET['sn']))) {
    // If no serial number is provided, exit.
    exit('No serial number provided.');
}

// Clean the input serial number
$serial_number = trim($_GET['sn']);

// 2. Create database connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    // In a real app, you'd log this error, not display it.
    exit('Connection failed.');
}

// 3. Perform the database lookup using a prepared statement
$stmt = $conn->prepare("SELECT status FROM devices WHERE serial_number = ?");
$stmt->bind_param("s", $serial_number);
$stmt->execute();
$result = $stmt->get_result();

// 4. & 5. Check the status and return the response
if ($result->num_rows > 0) {
    // Serial number was found
    $row = $result->fetch_assoc();
    $status = strtoupper(trim($row['status'])); // Trim status from DB as well, just in case

    if ($status === 'REGISTERED' || $status === 'ACTIVE') {
        echo "REGISTERED";
    } elseif ($status === 'BLOCKED') {
        echo "BLOCKED";
    } else {
        // For debugging, let's see what the actual status is
        // You can remove this line once the problem is solved
        echo "NOT REGISTERED" . $row['status'] . ")";
    }
} else {
    // 5. Serial number was not found
    echo "NOT REGISTERED";
}

// 6. Close connections
$stmt->close();
$conn->close();
?>
