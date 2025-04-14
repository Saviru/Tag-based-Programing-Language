<!-- User information example -->
<var name="currentDate">2025-04-14 02:22:11</var>
<var name="username">Saviru</var>

<print>========================</print>
<print>Welcome to TagLang System</print>
<print>========================</print>
<print>Current User: <var name="username" /></print>
<print>Login Time: <var name="currentDate" /></print>
<print>========================</print>

<!-- Create a User class -->
<class name="User">
    <var name="username">""</var>
    <var name="lastLogin">""</var>
    
    <method name="displayInfo">
        <print>User Information:</print>
        <print>  Username: <var name="this.username" /></print>
        <print>  Last Login: <var name="this.lastLogin" /></print>
    </method>
    
    <method name="calculateSessionTime">
        <var name="loginHour">parseInt(this.lastLogin.split(" ")[1].split(":")[0])</var>
        <var name="currentHour">parseInt(currentDate.split(" ")[1].split(":")[0])</var>
        <var name="sessionHours">currentHour - loginHour</var>
        <print>Session duration: <var name="sessionHours" /> hours</print>
    </method>
</class>

<!-- Create a user object -->
<new class="User" name="currentUser">
    <var name="username">username</var>
    <var name="lastLogin">currentDate</var>
</new>

<!-- Call methods on the user object -->
<callmethod object="currentUser" method="displayInfo"></callmethod>
<callmethod object="currentUser" method="calculateSessionTime"></callmethod>

<!-- Basic loop example -->
<print>========================</print>
<print>Loading system modules:</print>
<for var="i" from="1" to="5" step="1">
    <print>Module <var name="i" />: Loading... Complete!</print>
</for>
<print>System ready!</print>