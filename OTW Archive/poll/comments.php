<?php
global $HTTP_SERVER_VARS, $HTTP_GET_VARS, $HTTP_POST_VARS;
$include_path = dirname(__FILE__);
if ($include_path == "/") {
    $include_path = ".";
}

$id = (isset($HTTP_POST_VARS['id'])) ? intval($HTTP_POST_VARS['id']) : "";
if ($id == "") {
	if (isset($HTTP_GET_VARS['id'])) {
		$id = intval($HTTP_GET_VARS['id']);
	}
}

$template_set = (isset($HTTP_POST_VARS['template_set'])) ? trim($HTTP_POST_VARS['template_set']) : "";
if ($template_set == "") {
	if (isset($HTTP_GET_VARS['template_set'])) {
		$template_set = trim($HTTP_GET_VARS['template_set']);
	}
}

$action = (isset($HTTP_POST_VARS['action'])) ? trim($HTTP_POST_VARS['action']) : "";
if ($action == "") {
	if (isset($HTTP_GET_VARS['action'])) {
		$action = trim($HTTP_GET_VARS['action']);
	}
}

require $include_path."/include/config.inc.php";
require $include_path."/include/class_poll.php";
require $include_path."/include/class_pollcomment.php";

$my_comment = new pollcomment();

if (!empty($template_set)) {
    $my_comment->set_template_set("$template_set");
}
if (empty($id)) {
    echo $my_comment->print_message("Poll ID <b>".$id."</b> does not exist or is disabled!");
} elseif ($my_comment->is_comment_allowed($id)) {
    if ($action == "add") {
        $poll_input = array("message","name","email");
        for($i=0;$i<sizeof($poll_input);$i++) {
            if (isset($HTTP_POST_VARS[$poll_input[$i]])) {     
                $HTTP_POST_VARS[$poll_input[$i]] = trim($HTTP_POST_VARS[$poll_input[$i]]);    
            } else {
                $HTTP_POST_VARS[$poll_input[$i]] = '';
            }
        }
        if (empty($HTTP_POST_VARS['name'])) {
            echo $my_comment->print_message("Please enter your name.<br><a href=\"javascript:history.back()\">Go back</a>");
        }
        elseif (empty($HTTP_POST_VARS['message'])) {
            echo $my_comment->print_message("You forgot to fill in the message field!<br><a href=\"javascript:history.back()\">Go back</a>");
        }
    /*
        elseif (empty($HTTP_POST_VARS['email'])) {
            echo $my_comment->print_message("You must specify your e-mail address.!<br><a href=\"javascript:history.back()\">Go back</a>");
        }
    */
        else {
            $my_comment->add_comment($id);
            echo $my_comment->print_message("Your message has been sent!",1);
        }
    } else {
        echo $my_comment->poll_form($id);
    }
}

?>