#Example of TensorFlow libary
import tensorflow as tf

a = tf.placeholder(tf.float32)

b = tf.placeholder(tf.float32)

add = tf.add(a,b)

sess = tf.Session
bingding = {a:1.5,b:2.5}
c = sess.run(add,feed_dict = binding)
print (c)
